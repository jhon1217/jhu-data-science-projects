NEI <- readRDS("summarySCC_PM25.rds")
baltimore <- subset(NEI, fips == "24510")
totals <- aggregate(Emissions ~ year, data = baltimore, sum)
png("plot2.png", width = 900, height = 550)
plot(totals$year, totals$Emissions, type = "o", pch = 19, lwd = 2,
     col = "#0072B2", xlab = "Year", ylab = "PM2.5 emissions (tons)",
     main = "Baltimore City PM2.5 Emissions, 1999–2008", xaxt = "n")
axis(1, at = totals$year)
grid(nx = NA, ny = NULL, col = "grey85")
dev.off()
