library(ggplot2)
NEI <- readRDS("summarySCC_PM25.rds")
SCC <- readRDS("Source_Classification_Code.rds")
coal.codes <- SCC$SCC[grepl("Coal", SCC$EI.Sector, ignore.case = TRUE)]
coal <- subset(NEI, SCC %in% coal.codes)
totals <- aggregate(Emissions ~ year, data = coal, sum)
p <- ggplot(totals, aes(year, Emissions)) +
  geom_line(linewidth = 1, color = "#0072B2") + geom_point(size = 2.5, color = "#0072B2") +
  scale_x_continuous(breaks = c(1999, 2002, 2005, 2008)) +
  labs(title = "U.S. PM2.5 Emissions from Coal Combustion",
       x = "Year", y = "PM2.5 emissions (tons)") + theme_minimal(base_size = 12)
ggsave("plot4.png", p, width = 9, height = 5.5, dpi = 160)
