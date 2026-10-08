library(ggplot2)
NEI <- readRDS("summarySCC_PM25.rds")
baltimore <- subset(NEI, fips == "24510")
totals <- aggregate(Emissions ~ year + type, data = baltimore, sum)
p <- ggplot(totals, aes(year, Emissions, color = type, group = type)) +
  geom_line(linewidth = 1) + geom_point(size = 2.5) +
  scale_x_continuous(breaks = c(1999, 2002, 2005, 2008)) +
  labs(title = "Baltimore PM2.5 Emissions by Source Type",
       x = "Year", y = "PM2.5 emissions (tons)", color = "Source type") +
  theme_minimal(base_size = 12)
ggsave("plot3.png", p, width = 9, height = 5.5, dpi = 160)
