library(shiny)
ui_object <- source("ui.R", local=TRUE)$value
server_function <- source("server.R", local=TRUE)$value
shinyApp(ui=ui_object, server=server_function)
