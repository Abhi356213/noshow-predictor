#Prepare appointment data for the no-show model.
#Training and the API use the same preparation steps.

from pathlib import Path 
import pandas as pd

# Rename CSV columns for consistent names and correct spelling
RENAME = {
    "PatientId": "patient_id",
    "AppointmentID": "appointment_id",
    "Gender": "gender",
    "ScheduledDay": "scheduled_day",
    "AppointmentDay": "appointment_day",
    "Age": "age",
    "Neighbourhood": "neighbourhood",
    "Scholarship": "scholarship",
    "Hipertension": "hypertension",
    "Diabetes": "diabetes", 
    "Alcoholism": "alcoholism",
    "Handcap": "handicap",
    "SMS_received": "sms_received",
    "No-show": "no_show",
}

# Select the patient information the model uses to predict no-shows.
FEATURES = [
    "age",
    "is_female",
    "scholarship",
    "hypertension",
    "diabetes",
    "alcoholism",
    "handicap",
    "sms_received",
    "lead_days",
    "appt_weekday",
    "scheduled_hour",
    "prior_visits",
    "prior_noshows",
]

# Indentify the answer the model must predict:1 = missed, 0 = attended
TARGET = "no_show"

def load_raw(path: str | Path) -> pd.DataFrame:
   # Reads the kaggle CSV and fix names and types. funtion docstring

   # Read the file into a table.
   df = pd.read_csv(path)
 
   # Apply the renaming dictionary defined above.
   df = df.rename(columns=RENAME)

   # Turn "Yes"/"No" into 1/0, because models need numbers.
   # (Safe here: this function runs once per fresh load, so there's no
   # "ran the cell twice" problem like in the notebook.)
   df["no_show"] = (df["no_show"] == "Yes").astype(int)

   # Convert the date columns from text to real dates, 
   # -so we can subtract them.
   df["scheduled_day"] = pd.to_datetime(df["scheduled_day"])
   df["appointment_day"] = pd.to_datetime(df["appointment_day"])

   # "return" hands the finished table back to whoever called the function.
   return df

def _lead_days(df: pd.DataFrame) -> pd.Series:
   # Calendar days between booking and appointment.
   # .dt.normalize() drops the time of day, so we compare calendar days only.
   # .dt.days turns the time difference into a whole number of days.
   # A pd.Series is a single column (one value per row).
   return (
        df["scheduled_day"].dt.normalize() - df["scheduled_day"].dt.normalize() - df["scheduled_day"].dt.normalize()).dt.days

#dealing with the negative ones 
   def clean(df: pd.DataFrame) -> pd.DataFrame:
   #Drop impossible rows found in EDA: negative lead time or negative age
   # keep is a True/False column: True for rows that make sense.
    # "&" means AND: a row must pass BOTH checks to be kept.
    keep = (_lead_days(df) >= 0) & (df["age"] >= 0)

    # df[keep] keeps only the True rows.
    # reset_index(drop=True) renumbers rows 0, 1, 2... so there are no gaps
    # where removed rows used to be. drop=True throws the old numbers away.
   return df[keep].reset_index(drop=True) 


   def _add_patient_history(df: pd.DataFrame) -> pd.DataFrame: 
     #For each appointment, count the patient's visits and no-shows on EARLIER days.
     #We first collapse to one row per patient per day, so two appointments on the 
     #-same day can't see each other's outcome. That would leak information
    # STEP A: one row per patient per day.
    # groupby([...]) puts together all rows with the same patient AND same day.
    # .agg(visits="size", misses="sum") makes two new columns:
    #   visits = how many appointments that patient had that day
    #   misses = how many of them were no-shows (sum of 1s)
    # reset_index() turns patient_id and appointment_day back into normal columns.
    # sort_values(...) puts each patient's days in date order (oldest first),
    # which the running totals below depend on.
     daily = (
          df.groupby(["patient_id", "appointment_day"])
    ["no_show"]
          .agg(visits="size", misses="sum")
          .reset_index()
          .sort_values(["patient_id", "appointment_day"])  
     )

     by_patient = daily.groupby("patient_id") 

     