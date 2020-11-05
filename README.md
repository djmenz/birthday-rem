# birthday-rem
Birthday reminder script

### Summary
A simple script that is designed to be run daily, and emails out if it's someones birthday

### Deployment
The script is designed to run on AWS Lambda on a cron schedule, reads the list of people/birthday's from dynamoDB table, and uses SNS to send out the email if required.
