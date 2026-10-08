library(ggplot2)
NEI <- readRDS("summarySCC_PM25.rds")
SCC <- readRDS("Source_Classification_Code.rds")
vehicle.codes <- SCC$SCC[grepl("Mobile - On-Road", SCC$EI.Sector, ignore.case = TRUE)]
vehicles <- subset(NEI, SCC %in% vehicle.codes & fips %in% c("24510", "06037"))
vehicles$city <- factor(vehicles$fips, levels = c("24510", "06037"),
                        labels = c("Baltimore City", "Los Angeles County"))
totals <- aggregate(Emissions ~ year + city, data = vehicles, sum)
p <- ggplot(totals, aes(year, Emissions, color = city, group = city)) +
  geom_line(linewidth = 1) + geom_point(size = 2.5) +
  scale_x_continuous(breaks = c(1999, 2002, 2005, 2008)) +
  labs(title = "Motor-Vehicle PM2.5: Baltimore vs. Los Angeles",
       x = "Year", y = "PM2.5 emissions (tons)", color = "Area") +
  theme_minimal(base_size = 12)
ggsave("plot6.png", p, width = 9, height = 5.5, dpi = 160)
