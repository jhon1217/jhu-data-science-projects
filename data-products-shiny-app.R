library(shiny)

fuel_model <- lm(mpg ~ wt + hp + am, data = mtcars)

ui <- fluidPage(
  titlePanel("Fuel Economy Scenario Explorer"),
  sidebarLayout(
    sidebarPanel(
      sliderInput("weight", "Vehicle weight (1,000 lb)", min = 1.5, max = 5.5,
                  value = 3.0, step = 0.1),
      sliderInput("horsepower", "Horsepower", min = 50, max = 350,
                  value = 150, step = 5),
      radioButtons("transmission", "Transmission",
                   choices = c("Automatic" = 0, "Manual" = 1), inline = TRUE),
      helpText("Predictions use lm(mpg ~ wt + hp + am) fitted to the built-in mtcars data.")
    ),
    mainPanel(
      h2(textOutput("prediction", inline = TRUE)),
      plotOutput("context_plot", height = "460px"),
      p("The highlighted point shows the selected scenario against the observed vehicles.")
    )
  )
)

server <- function(input, output, session) {
  scenario <- reactive({
    data.frame(wt = input$weight, hp = input$horsepower,
               am = as.numeric(input$transmission))
  })

  predicted_mpg <- reactive(as.numeric(predict(fuel_model, newdata = scenario())))

  output$prediction <- renderText({
    sprintf("Predicted fuel economy: %.1f MPG", predicted_mpg())
  })

  output$context_plot <- renderPlot({
    transmission_colors <- ifelse(mtcars$am == 1, "#7c3aed", "#0891b2")
    plot(mtcars$wt, mtcars$mpg, pch = 19, col = transmission_colors,
         xlab = "Vehicle weight (1,000 lb)", ylab = "Fuel economy (MPG)",
         main = "Selected scenario in the observed mtcars range")
    points(input$weight, predicted_mpg(), pch = 21, cex = 2.2,
           bg = "#f59e0b", col = "#111827", lwd = 2)
    legend("topright", c("Automatic", "Manual", "Selected scenario"),
           col = c("#0891b2", "#7c3aed", "#111827"),
           pt.bg = c("#0891b2", "#7c3aed", "#f59e0b"),
           pch = c(19, 19, 21), bty = "n")
  })
}

shinyApp(ui = ui, server = server)
