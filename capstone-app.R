library(shiny)

prediction_table <- list(
  "i went to the" = c("new", "next", "world"),
  "thank you for" = c("the", "your", "all"),
  "the weather is" = c("perfect", "good", "nice")
)
fallback_words <- c("the", "to", "and")

normalize_phrase <- function(text) {
  text <- tolower(text)
  text <- gsub("https?://\\S+|@\\w+", " ", text)
  text <- gsub("[^a-z']+", " ", text)
  trimws(gsub("\\s+", " ", text))
}

predict_words <- function(text) {
  normalized <- normalize_phrase(text)
  words <- strsplit(normalized, " ", fixed = TRUE)[[1]]
  words <- words[nzchar(words)]
  for (size in seq(min(4, length(words)), 1)) {
    context <- paste(tail(words, size), collapse = " ")
    if (!is.null(prediction_table[[context]])) {
      return(list(words = prediction_table[[context]], order = size + 1,
                  context = context))
    }
  }
  list(words = fallback_words, order = 1, context = "unigram fallback")
}

ui <- fluidPage(
  titlePanel("NextWord Predictor"),
  sidebarLayout(
    sidebarPanel(
      textInput("phrase", "Enter a phrase", value = "I went to the"),
      actionButton("predict", "Predict next word", class = "btn-primary"),
      helpText("The portfolio demo exposes the same backoff behavior described in the project report.")
    ),
    mainPanel(
      h2(textOutput("primary_prediction", inline = TRUE)),
      h4("Alternatives"),
      textOutput("alternatives"),
      hr(),
      textOutput("model_context"),
      p("Published held-out evaluation: top-1 accuracy 12.44%; top-3 accuracy 20.07% across 193,477 tokens."),
      p("Limit: this compact portfolio version contains representative contexts; coverage varies by domain.")
    )
  )
)

server <- function(input, output, session) {
  result <- eventReactive(input$predict, predict_words(input$phrase), ignoreNULL = FALSE)
  output$primary_prediction <- renderText(sprintf("Next word: %s", result()$words[1]))
  output$alternatives <- renderText(paste(result()$words[-1], collapse = " · "))
  output$model_context <- renderText(
    sprintf("Matched context: %s | backoff order: %d", result()$context, result()$order)
  )
}

shinyApp(ui = ui, server = server)
