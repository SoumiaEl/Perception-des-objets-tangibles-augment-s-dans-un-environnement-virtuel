library(tidyverse)
library(hrbrthemes)
library(cluster)  
library(factoextra)  
library(stringr)  
library(ggplot2)
library(dplyr)
library(dplyr)
library(car)
library(carData)
library(tidyverse)
library(hrbrthemes)
library(ARTool)  # Pour ART ANOVA
library(ggplot2)


participants <- c(2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)

# Initialiser un dataframe 
all_data <- data.frame()

# Charger, nettoyer, normaliser et agréger les données de tous les participants
for (participant_id in participants) {
  
  csv_file_path <- paste0("data/Results/Participant_", participant_id, ".csv")
  dat_file_path <- paste0("data/Results/Participant_", participant_id, ".dat")
  
  
  data_csv <- read.csv(csv_file_path, header = FALSE, col.names = c("Amplitude", "Frequency", "Texture"))
  data_dat <- read.csv(dat_file_path, header = FALSE, col.names = c("RawData"), stringsAsFactors = FALSE)
  
  
  data_dat_cleaned <- data_dat[-1, , drop = FALSE]  
  data_dat_split <- data_dat_cleaned %>% 
    separate(RawData, into = c("Index", "Roughness", "Vibration_Intensity"), sep = "\t", convert = TRUE) %>% 
    select(-Index)
  
  
  data_csv_cleaned <- data_csv[-1, , drop = FALSE]  
  data_csv_cleaned <- data_csv_cleaned %>% 
    mutate(Amplitude = as.numeric(Amplitude),
           Frequency = as.integer(Frequency),
           Texture = as.numeric(Texture))
  
  # Fusionner les données CSV et DAT
  participant_data <- bind_cols(data_csv_cleaned, data_dat_split)
  
  # Normaliser les données pour chaque participant entre 0 et 1
  participant_data <- participant_data %>%
    mutate(Roughness = (Roughness - min(Roughness)) / (max(Roughness) - min(Roughness)),
           Vibration_Intensity = (Vibration_Intensity - min(Vibration_Intensity)) / (max(Vibration_Intensity) - min(Vibration_Intensity)))
  
  
  participant_data_median <- participant_data %>%
    group_by(Amplitude, Frequency, Texture) %>%
    summarize(Roughness = median(Roughness, na.rm = TRUE),
              Vibration_Intensity = median(Vibration_Intensity, na.rm = TRUE)) %>%
    ungroup() %>%
    mutate(Participant = as.factor(participant_id))  
  
  
  all_data <- bind_rows(all_data, participant_data_median)
}

# Normaliser les données globales (Amplitude et Roughness) 
all_data_scaled <- scale(all_data %>% select(Amplitude, Roughness))


###############

# Créer un boxplot de la perception de la rugosité en fonction des textures et des fréquences


###############

p_boxplot <- ggplot(all_data, aes(x = as.factor(Texture), y = Roughness, fill = as.factor(Frequency))) +
  geom_boxplot(alpha = 0.5, color = "black", position = position_dodge(width = 0.75)) +  
  labs(title = str_wrap("Average Roughness Perception by Texture and Frequency for All Participants", width = 50),  
       x = "Hair Length (mm)",  
       y = "Roughness",
       fill = "Frequency (Hz)") + 
  scale_y_continuous(limits = c(0, 1)) +  
  theme_minimal() +
  theme(
    axis.title.x = element_text(size = 14, hjust = 0.5),  
    axis.title.y = element_text(size = 14, hjust = 0.5, angle = 90),  
    axis.text.x = element_text(size = 14), 
    axis.text.y = element_text(size = 14),  
    plot.title = element_text(hjust = 0.5, size = 18)  
  )


print(p_boxplot)


ggsave(filename = "Boxplot_Rugosity_Texture_Frequency_All_Participants.png", plot = p_boxplot, width = 7, height = 7)

#######################

# Modèle linéaire pour examiner la relation entre l'intensité des vibrations et la perception de la rugosité

#######################


model_intensity_roughness <- lm(Roughness ~ Vibration_Intensity, data = all_data)

# Résumé du modèle
summary(model_intensity_roughness)

# Créer un graphique de dispersion pour la rugosité en fonction de l'intensité des vibrations
p_intensity_roughness <- ggplot(all_data, aes(x = Vibration_Intensity, y = Roughness)) +
  geom_point(size = 3, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE, linetype = "dashed", color = "blue") +  
  labs(title = str_wrap(paste("Relation between the Perception of Roughness and the Perceived Vibration Intensity"), width = 50),
       x = "Perceived Vibration Intensity",
       y = "Roughness") +
  scale_y_continuous(limits = c(0, 1)) +  
  theme_minimal() +
  theme(
    axis.title.x = element_text(size = 14, hjust = 0.5),  
    axis.title.y = element_text(size = 14, hjust = 0.5, angle = 90),  
    axis.text.x = element_text(size = 14), 
    axis.text.y = element_text(size = 14), 
    plot.title = element_text(hjust = 0.5, size = 18) 
  )


print(p_intensity_roughness)



ggsave(filename = "Intensity_vs_Roughness.png", plot = p_intensity_roughness, width = 7, height = 7)

# Vérification de la normalité des réponses pour chaque combinaison de texture et de fréquence
normality_tests <- all_data %>%
  group_by(Texture, Frequency) %>%
  summarize(
    shapiro_p_value = shapiro.test(Roughness)$p.value
  )

# Afficher les résultats des tests de Shapiro-Wilk
print(normality_tests)



# Effectuer le test de Shapiro-Wilk pour chaque combinaison de Texture et Frequency
normality_tests <- all_data %>%
  group_by(Texture, Frequency) %>%
  summarise(shapiro_p_value = shapiro.test(Roughness)$p.value)


all_data <- all_data %>%
  left_join(normality_tests, by = c("Texture", "Frequency"))

# Filtrer les données qui suivent une distribution normale
normal_data <- all_data %>%
  filter((Texture == 2.5 & Frequency == 80 & shapiro_p_value > 0.05) |
           (Texture == 5.0 & Frequency == 160 & shapiro_p_value > 0.05) |
           (Texture == 7.5 & Frequency == 160 & shapiro_p_value > 0.05) |
           (Texture == 10.0 & Frequency == 160 & shapiro_p_value > 0.05))


###################

#ART Anova
###############################

# Convertir les variables en facteurs
all_data <- all_data %>%
  mutate(
    Amplitude = as.factor(Amplitude),
    Frequency = as.factor(Frequency),
    Texture = as.factor(Texture)
  )


# Réaliser l'ART ANOVA
art_model <- art(Roughness ~ Amplitude * Frequency * Texture + (1 | Participant), data = all_data)

# Résumé des résultats de l'ART ANOVA
anova_results <- anova(art_model)

# Afficher les résultats de l'ART ANOVA
print(anova_results)




# Assurez-vous que les variables sont des facteurs
all_data <- all_data %>%
  mutate(
    Amplitude = as.factor(Amplitude),
    Frequency = as.factor(Frequency),
    Texture = as.factor(Texture)
  )

# Filtrer les données par niveau de fréquence
frequency_levels <- unique(all_data$Frequency)

for (freq in frequency_levels) {
  # Filtrer les données pour chaque fréquence
  data_subset <- all_data %>% filter(Frequency == freq)
  
  # Réaliser l'ART ANOVA pour l'effet de l'amplitude à ce niveau de fréquence
  art_model <- art(Roughness ~ Amplitude * Texture + (1 | Participant), data = data_subset)
  anova_results <- anova(art_model)
  
  # Afficher les résultats pour cette fréquence
  cat("Résultats pour la fréquence :", freq, "\n")
  print(anova_results)
  cat("\n")
}









