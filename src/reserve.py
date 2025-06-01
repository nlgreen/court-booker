import requests
from datetime import datetime, timedelta
import json
import os
import sys

allowed_day = "Sunday"
start_time = "20:00:00"
duration = "90"

def load_auth_data():
    """Load auth data from auth.json. Exit if file doesn't exist."""
    if not os.path.exists("auth.json"):
        print("Error: auth.json not found. Please run login.py first to generate auth data.")
        sys.exit(1)
        
    try:
        with open("auth.json", "r") as f:
            auth_data = json.load(f)
            return auth_data["request_data"], auth_data["verification_token"]
    except Exception as e:
        print(f"Error reading auth.json: {str(e)}")
        sys.exit(1)

def run():
    # Load auth data first
    request_data, request_verification_token = load_auth_data()
    
    current_date = datetime.now()
    day_of_week = current_date.strftime("%A")
    if day_of_week != allowed_day:
        print("Day is " + day_of_week + " but allowed day is " + allowed_day + ". Sleeping.")
        return

    desired_date = (current_date + timedelta(days=8)).strftime("%-m/%-d/%y") + " 12:00:00 AM"
    print("Attempting to book " + desired_date)

    send_reservation_request(desired_date, request_data, request_verification_token)


def send_reservation_request(date, request_data, request_verification_token):
    url = "https://reservations.courtreserve.com//Online/ReservationsApi/CreateReservation/12465?uiCulture=en-US"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://app.courtreserve.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://app.courtreserve.com/",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    data = {
        "__RequestVerificationToken": request_verification_token,
        "Id": "12465",
        "OrgId": "12465",
        "MemberId": "6639532",
        "MemberIds": "",
        "IsConsolidatedScheduler": "True",
        "HoldTimeForReservation": "15",
        "RequirePaymentWhenBookingCourtsOnline": "False",
        "AllowMemberToPickOtherMembersToPlayWith": "False",
        "ReservableEntityName": "Court",
        "IsAllowedToPickStartAndEndTime": "False",
        "CustomSchedulerId": "16819",
        "IsConsolidated": "True",
        "IsToday": "False",
        "IsFromDynamicSlots": "False",
        "InstructorId": "",
        "InstructorName": "",
        "CanSelectCourt": "False",
        "IsCourtRequired": "False",
        "CostTypeAllowOpenMatches": "False",
        "IsMultipleCourtRequired": "False",
        "ReservationQueueId": "",
        "ReservationQueueSlotId": "",
        "RequestData": request_data,
        "IsMobileLayout": "False",
        "Date": date,
        "SelectedCourtType": "Hard",
        "SelectedCourtTypeId": "2",
        "SelectedResourceId": "",
        "DisclosureName": "Court Reservations",
        "IsResourceReservation": "False",
        "StartTime": start_time,
        "CourtTypeEnum": "2",
        "MembershipId": "139864",
        "UseMinTimeByDefault": "False",
        "IsEligibleForPreauthorization": "False",
        "MatchMakerSelectedRatingIdsString": "",
        "DurationType": "",
        "MaxAllowedCourtsPerReservation": "1",
        "SelectedResourceName": "",
        "ReservationTypeId": "61740",
        "Duration": duration,
        "CourtId": "",
        "OwnersDropdown_input": "",
        "OwnersDropdown": "",
        "SelectedMembers[0].OrgMemberId": "5674663",
        "SelectedMembers[0].MemberId": "6639532",
        "SelectedMembers[0].OrgMemberFamilyId": "1443904",
        "SelectedMembers[0].FirstName": "Nathaniel",
        "SelectedMembers[0].LastName": "Green",
        "SelectedMembers[0].Email": "Nathanielg.95@gmail.com",
        "SelectedMembers[0].MembershipNumber": "5674663",
        "SelectedMembers[0].PaidAmt": "",
        "SelectedMembers[0].PriceToPay": "16.5",
        "SelectedNumberOfGuests": "",
        "DisclosureAgree": "true"
    }

    response = requests.post(url, headers=headers, data=data)

    print("Status Code:", response.status_code)
    data = json.loads(response.text)
    is_valid = data.get("isValid")
    if not is_valid:
        print("Response Text:", response.text)
    else:
        print("Success")

run()
