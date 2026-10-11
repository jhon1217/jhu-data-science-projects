# Activity Monitoring: Daily Patterns and Missing-Value Imputation

*Reproducible Research course project*


```r
knitr::opts_chunk$set(echo = TRUE, fig.width = 8, fig.height = 5)
```

## Loading and preprocessing the data

The analysis starts from the supplied `activity.csv`. Dates are converted to R's Date class.

```r
activity <- read.csv("data/activity.csv", stringsAsFactors = FALSE)
activity$date <- as.Date(activity$date)
```

## What is the mean total number of steps taken per day?

Missing observations are ignored for this first calculation. Days containing only missing observations are therefore excluded from the summary.

```r
daily <- aggregate(steps ~ date, activity, sum, na.rm = TRUE)
hist(daily$steps, breaks = 12, col = "#0072B2",
     main = "Total Steps per Day", xlab = "Steps")
mean(daily$steps)
median(daily$steps)
```

![Output for daily-total](figure/daily_steps.png)


The mean daily total is approximately **10,766.19 steps** and the median is **10,765 steps**.

## What is the average daily activity pattern?

```r
pattern <- aggregate(steps ~ interval, activity, mean, na.rm = TRUE)
plot(pattern$interval, pattern$steps, type = "l", col = "#0072B2", lwd = 2,
     main = "Average Daily Activity Pattern", xlab = "5-minute interval",
     ylab = "Average steps")
pattern$interval[which.max(pattern$steps)]
max(pattern$steps)
```

![Output for pattern](figure/activity_pattern.png)


Interval **835** has the largest average, approximately **206.17 steps**.

## Imputing missing values

There are **2,304** missing step observations. Each missing value is replaced with the mean for its 5-minute interval across all observed days. This retains the daily time profile while avoiding an arbitrary zero replacement.

```r
sum(is.na(activity$steps))
interval.means <- tapply(activity$steps, activity$interval, mean, na.rm = TRUE)
activity.imputed <- activity
missing <- is.na(activity.imputed$steps)
activity.imputed$steps[missing] <- interval.means[as.character(activity.imputed$interval[missing])]
daily.imputed <- aggregate(steps ~ date, activity.imputed, sum)
hist(daily.imputed$steps, breaks = 12, col = "#009E73",
     main = "Total Steps per Day after Imputation", xlab = "Steps")
mean(daily.imputed$steps)
median(daily.imputed$steps)
```

![Output for impute](figure/daily_steps_imputed.png)


After imputation, the mean is approximately **10,766.19** and the median is **10,766.19** steps. The mean is unchanged because interval means were used. The median moves slightly and formerly missing days are restored to the distribution.

## Are there differences between weekdays and weekends?

```r
activity.imputed$day.type <- factor(ifelse(weekdays(activity.imputed$date) %in% c("Saturday", "Sunday"), "weekend", "weekday"), levels = c("weekday", "weekend"))
patterns <- aggregate(steps ~ interval + day.type, activity.imputed, mean)
par(mfrow = c(2, 1), mar = c(4, 4, 3, 1))
for (d in levels(patterns$day.type)) {
  x <- subset(patterns, day.type == d)
  plot(x$interval, x$steps, type = "l", lwd = 2,
       col = ifelse(d == "weekday", "#0072B2", "#D55E00"),
       main = paste("Average activity:", d), xlab = "5-minute interval",
       ylab = "Average steps")
}
par(mfrow = c(1, 1))
```

![Output for weekday-weekend](figure/weekday_weekend.png)


Weekdays show a sharper morning peak, while weekend activity is distributed more broadly later in the day. The plot supports a difference in timing and shape, without implying a causal explanation.
