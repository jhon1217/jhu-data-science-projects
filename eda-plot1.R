NEI <- readRDS("summarySCC_PM25.rds")
totals <- aggregate(Emissions ~ year, data = NEI, sum)
png("plot1.png", width = 900, height = 550)
plot(totals$year, totals$Emissions, type = "o", pch = 19, lwd = 2,
     col = "#0072B2", xlab = "Year", ylab = "PM2.5 emissions (tons)",
     main = "Total U.S. PM2.5 Emissions, 1999–2008", xaxt = "n")
axis(1, at = totals$year)
grid(nx = NA, ny = NULL, col = "grey85")
dev.off()
