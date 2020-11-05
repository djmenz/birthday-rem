from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import csv
from datetime import datetime, timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import operator

# 4. Get it running in AWS Lambda (ensure time zone is correct)
# 5. Put on a schedule in AWS Lambda

def send_notification_email(email_body, person):

	today_dt = datetime.today() + timedelta(hours=10)
	today_formatted = today_dt.strftime("%d %B %Y")

	msg_client = boto3.client('sns',region_name='us-west-2')
	topic = msg_client.create_topic(Name="crypto-news-daily")
	topic_arn = topic['TopicArn']  # get its Amazon Resource Name
	mail_subject = f"Birthday Reminder: {today_formatted} - {person}"

	msg_client.publish(TopicArn=topic_arn,Message=email_body,Subject=mail_subject)


def main():

	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
	table = dynamodb.Table('birthday_store')
	full_table = table.scan()

	#today = date.today()
	
	#today_dt = datetime.today() + timedelta(hours=9)
	today_dt = datetime.today()
	print(f"Today's date {today_dt} \n")

	people = []
	
	for person in (full_table['Items']):
		person_dict = {}
		name = person['name']
		birthday = person['birthday']

		uncertain = False
		if birthday.find("?") != -1:
			uncertain = True

		birthday = birthday.strip("?")

		#print(f"{name} {birthday}")
		person_dict['name'] = name
		person_dict['birthday'] = birthday
		
		temp_date = datetime.strptime(birthday, "%d/%B/%Y")

		temp_age = (abs(today_dt - temp_date).days)/365.2425
		temp_age_years = relativedelta(today_dt, temp_date).years
		temp_age_months = relativedelta(today_dt, temp_date).months

		#print(f"{temp_age_years}, {temp_age_months} months\n")
		person_dict['years_old'] = temp_age_years
		person_dict['months_old'] = temp_age_months

		if ((temp_date.day == today_dt.day) and (temp_date.month == today_dt.month)):
			
			# Birthday Found
			notification = (f"It is {name}'s birthday today. They are {temp_age_years} Years old.")
			if uncertain:
				notification += f" - Not 100% sure on this"

			print(notification)
			send_notification_email(notification, name)

		people.append(person_dict)

	people2 = sorted(people, key=lambda k: (k['months_old'], -int(k['birthday'].split("/")[0])))
	people2.reverse()

	for person in people2:

		print(f"{person['name']} {person['birthday']}")
		print(f"{person['years_old']}, {person['months_old']} months\n")



if __name__ == '__main__':
	main()
