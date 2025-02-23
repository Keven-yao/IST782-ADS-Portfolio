#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    https://shiny.posit.co/
#

library(DT)
library(rsconnect)

# Define UI for application that draws a histogram

# Load required libraries
library(shiny)
library(ggplot2)
library(caret) # For modeling

# Load data
data <- read.csv("/Users/surabhiarchitha/Project_Group5/shiny_Data.csv")


# Check and clean the dataset
if (!"Total_Energy_Usage" %in% colnames(data)) {
  stop("Column 'Total_Energy_Usage' not found in the dataset.")
}

# Remove rows with missing Total_Energy_Usage values
data <- data[!is.na(data$Total_Energy_Usage), ]

# Ensure at least 2 data points
if (nrow(data) < 2) {
  stop("Not enough data points in 'Total_Energy_Usage' for partitioning.")
}

# Preprocess and split the data
set.seed(123)
train_index <- createDataPartition(data$Total_Energy_Usage, p = 0.8, list = FALSE)
train_data <- data[train_index, ]
test_data <- data[-train_index, ]

# Train a model
model <- train(
  Total_Energy_Usage ~ out.electricity.cooling.energy_consumption +
    out.electricity.cooling_fans_pumps.energy_consumption +
    out.electricity.plug_loads.energy_consumption +
    out.electricity.lighting_interior.energy_consumption +
    in.sqft +
    Dry_Bulb_Temperature,
  data = train_data,
  method = "lm"
)

# Define UI
ui <- fluidPage(
  titlePanel("Energy Usage Prediction App"),
  
  sidebarLayout(
    sidebarPanel(
      numericInput("cooling_energy", "Cooling Energy Consumption:", value = 0.5, min = 0, step = 0.1),
      numericInput("cooling_fans_pumps", "Cooling Fans/Pumps Energy Consumption:", value = 0.5, min = 0, step = 0.1),
      numericInput("plug_loads", "Plug Loads Energy Consumption:", value = 0.5, min = 0, step = 0.1),
      numericInput("lighting_interior", "Lighting Interior Energy Consumption:", value = 0.5, min = 0, step = 0.1),
      numericInput("sqft", "House Square Footage:", value = 1500, min = 0, step = 100),
      numericInput("temperature", "Dry Bulb Temperature:", value = 25, min = 0, step = 1),
      actionButton("predict", "Predict")
    ),
    
    mainPanel(
      h3("Prediction Results"),
      textOutput("prediction"),
      plotOutput("plot_actual_vs_predicted"),
      br(),
      h3("Model Summary"),
      verbatimTextOutput("model_summary")
    )
  )
)

# Server
server <- function(input, output) {
  # Model summary
  output$model_summary <- renderPrint({
    summary(model$finalModel) # Access the final model for summary
  })
  
  # Prediction logic
  observeEvent(input$predict, {
    # Create a new data frame with user inputs
    new_data <- data.frame(
      out.electricity.cooling.energy_consumption = input$cooling_energy,
      out.electricity.cooling_fans_pumps.energy_consumption = input$cooling_fans_pumps,
      out.electricity.plug_loads.energy_consumption = input$plug_loads,
      out.electricity.lighting_interior.energy_consumption = input$lighting_interior,
      in.sqft = input$sqft,
      Dry_Bulb_Temperature = input$temperature
    )
    
    # Predict energy usage
    prediction <- predict(model, newdata = new_data)
    
    # Display prediction
    output$prediction <- renderText({
      paste("Predicted Total Energy Usage:", round(prediction, 2))
    })
  })
  
  # Actual vs. Predicted plot
  output$plot_actual_vs_predicted <- renderPlot({
    predictions <- predict(model, newdata = test_data)
    test_data$predicted_usage <- predictions
    
    ggplot(test_data, aes(x = Total_Energy_Usage, y = predicted_usage)) +
      geom_point(alpha = 0.5) +
      geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed") +
      labs(title = "Predicted vs Actual Energy Usage",
           x = "Total Energy Usage", y = "Predicted Energy Usage") +
      theme_minimal()
  })
}


# Run the app
shinyApp(ui = ui, server = server)
