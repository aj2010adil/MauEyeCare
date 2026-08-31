import os
import json
import re
import uuid
from datetime import datetime, timedelta, date

FOLLOWUPS_FILE = os.path.join(os.path.dirname(__file__), "..", "followups_data.json")

def parse_relative_interval(review_str: str, from_date: date = None) -> date:
    """Calculate exact target date based on doctor's review interval string"""
    if from_date is None:
        from_date = datetime.now().date()
        
    if isinstance(from_date, datetime):
        from_date = from_date.date()
        
    s = (review_str or "").lower().strip()
    
    if not s or "sos" in s or "as needed" in s:
        return None
        
    # Check common intervals
    if "1 week" in s or "7 day" in s:
        return from_date + timedelta(days=7)
    elif "10 day" in s:
        return from_date + timedelta(days=10)
    elif "15 day" in s or "2 week" in s:
        return from_date + timedelta(days=15)
    elif "3 week" in s or "21 day" in s:
        return from_date + timedelta(days=21)
    elif "1 month" in s or "30 day" in s or "4 week" in s:
        return from_date + timedelta(days=30)
    elif "2 month" in s or "60 day" in s:
        return from_date + timedelta(days=60)
    elif "3 month" in s or "90 day" in s:
        return from_date + timedelta(days=90)
    elif "6 month" in s or "180 day" in s:
        return from_date + timedelta(days=180)
    elif "1 year" in s or "annual" in s or "12 month" in s or "365 day" in s:
        return from_date + timedelta(days=365)
        
    # Try regex match for generic "X days/weeks/months"
    match_days = re.search(r'(\d+)\s*day', s)
    if match_days:
        return from_date + timedelta(days=int(match_days.group(1)))
        
    match_weeks = re.search(r'(\d+)\s*week', s)
    if match_weeks:
        return from_date + timedelta(days=int(match_weeks.group(1)) * 7)
        
    match_months = re.search(r'(\d+)\s*month', s)
    if match_months:
        return from_date + timedelta(days=int(match_months.group(1)) * 30)

    # Try ISO date parsing (YYYY-MM-DD or DD/MM/YYYY)
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
            
    # Default fallback to 30 days
    return from_date + timedelta(days=30)


class FollowupManager:
    def __init__(self, storage_path=FOLLOWUPS_FILE):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
            except Exception:
                pass

    def _load_data(self):
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Deduplicate and ensure unique IDs for every item
                    seen_ids = set()
                    modified = False
                    for idx, item in enumerate(data):
                        cur_id = item.get("id")
                        if not cur_id or cur_id in seen_ids:
                            item["id"] = f"FU-{uuid.uuid4().hex[:10]}"
                            modified = True
                        seen_ids.add(item["id"])
                    if modified:
                        self._save_data(data)
                    return data
        except Exception:
            pass
        return []

    def _save_data(self, data):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def add_followup(self, patient_name, mobile, consultation_date=None, review_interval="After 1 Month", diagnosis="", advice=""):
        """Add or update a patient follow-up entry"""
        if not patient_name:
            return None
            
        data = self._load_data()
        
        if consultation_date is None:
            consult_d = datetime.now().date()
        elif isinstance(consultation_date, str):
            try:
                consult_d = datetime.strptime(consultation_date[:10], "%Y-%m-%d").date()
            except ValueError:
                try:
                    consult_d = datetime.strptime(consultation_date[:10], "%d/%m/%Y").date()
                except ValueError:
                    consult_d = datetime.now().date()
        elif isinstance(consultation_date, datetime):
            consult_d = consultation_date.date()
        else:
            consult_d = consultation_date
            
        target_date = parse_relative_interval(review_interval, consult_d)
        target_date_str = target_date.strftime("%Y-%m-%d") if target_date else ""
        
        # Check if already exists for this patient & consultation date
        for entry in data:
            if entry.get("patient_name", "").lower() == patient_name.lower() and entry.get("consultation_date") == consult_d.strftime("%Y-%m-%d"):
                entry["mobile"] = mobile or entry.get("mobile", "")
                entry["review_interval"] = review_interval
                entry["target_date"] = target_date_str
                entry["diagnosis"] = diagnosis or entry.get("diagnosis", "")
                entry["advice"] = advice or entry.get("advice", "")
                entry["status"] = "Pending"
                self._save_data(data)
                return entry
                
        # Create new entry with guaranteed unique UUID
        new_entry = {
            "id": f"FU-{uuid.uuid4().hex[:10]}",
            "patient_name": patient_name,
            "mobile": mobile or "",
            "consultation_date": consult_d.strftime("%Y-%m-%d"),
            "review_interval": review_interval,
            "target_date": target_date_str,
            "diagnosis": diagnosis,
            "advice": advice,
            "status": "Pending",  # 'Pending', 'Reminder Sent', 'Completed'
            "reminders_count": 0,
            "last_reminder_sent_at": "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        data.insert(0, new_entry)
        self._save_data(data)
        return new_entry

    def get_all_followups(self):
        """Retrieve all followups sorted by target date"""
        data = self._load_data()
        return data

    def get_categorized_followups(self, reference_date=None):
        """Categorize active followups into Overdue, Due Today, Upcoming Week, Upcoming Month, and Completed"""
        if reference_date is None:
            reference_date = datetime.now().date()
            
        data = self._load_data()
        
        overdue = []
        due_today = []
        upcoming_week = []
        upcoming_month = []
        completed = []
        sos = []
        
        for item in data:
            if item.get("status") == "Completed":
                completed.append(item)
                continue
                
            t_str = item.get("target_date")
            if not t_str:
                sos.append(item)
                continue
                
            try:
                t_date = datetime.strptime(t_str, "%Y-%m-%d").date()
                diff_days = (t_date - reference_date).days
                item["diff_days"] = diff_days
                
                if diff_days < 0:
                    overdue.append(item)
                elif diff_days == 0:
                    due_today.append(item)
                elif 0 < diff_days <= 7:
                    upcoming_week.append(item)
                else:
                    upcoming_month.append(item)
            except Exception:
                sos.append(item)
                
        # Sort lists
        overdue.sort(key=lambda x: x.get("target_date", ""))
        due_today.sort(key=lambda x: x.get("patient_name", ""))
        upcoming_week.sort(key=lambda x: x.get("target_date", ""))
        upcoming_month.sort(key=lambda x: x.get("target_date", ""))
        
        return {
            "overdue": overdue,
            "due_today": due_today,
            "upcoming_week": upcoming_week,
            "upcoming_month": upcoming_month,
            "completed": completed,
            "sos": sos,
            "total_active": len(overdue) + len(due_today) + len(upcoming_week) + len(upcoming_month)
        }

    def mark_reminder_sent(self, followup_id):
        """Update follow-up status when WhatsApp reminder is sent"""
        data = self._load_data()
        for item in data:
            if item.get("id") == followup_id:
                item["status"] = "Reminder Sent"
                item["reminders_count"] = item.get("reminders_count", 0) + 1
                item["last_reminder_sent_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data(data)
                return True
        return False

    def mark_completed(self, followup_id):
        """Mark patient review as completed / visited"""
        data = self._load_data()
        for item in data:
            if item.get("id") == followup_id:
                item["status"] = "Completed"
                item["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data(data)
                return True
        return False

    def reschedule(self, followup_id, new_target_date_or_interval):
        """Reschedule follow-up to a new date or interval"""
        data = self._load_data()
        for item in data:
            if item.get("id") == followup_id:
                target_date = parse_relative_interval(new_target_date_or_interval, datetime.now().date())
                if target_date:
                    item["target_date"] = target_date.strftime("%Y-%m-%d")
                    item["review_interval"] = new_target_date_or_interval
                    item["status"] = "Pending"
                    self._save_data(data)
                    return True
        return False

    def delete_followup(self, followup_id):
        """Delete follow-up record"""
        data = self._load_data()
        new_data = [item for item in data if item.get("id") != followup_id]
        if len(new_data) != len(data):
            self._save_data(new_data)
            return True
        return False

    def auto_import_from_patients(self, patients_list):
        """Automatically seed follow-up queue from past patient records with unique UUIDs"""
        if not patients_list:
            return 0
            
        data = self._load_data()
        existing_keys = {f"{item.get('patient_name', '').lower()}-{item.get('consultation_date', '')}" for item in data}
        imported_count = 0
        
        for p in patients_list:
            if not isinstance(p, dict):
                continue
            name = p.get("name", "").strip()
            if not name:
                continue
                
            mobile = p.get("mobile", "")
            reg_date_str = p.get("registration_date", "") or datetime.now().strftime("%Y-%m-%d")
            reg_d_clean = reg_date_str[:10]
            
            key = f"{name.lower()}-{reg_d_clean}"
            if key not in existing_keys:
                advice = p.get("advice", "")
                issue = p.get("issue", "")
                
                # Default review interval if not specified
                review_interval = "After 1 Month"
                if "1 week" in advice.lower() or "7 day" in advice.lower():
                    review_interval = "After 1 Week"
                elif "15 day" in advice.lower() or "2 week" in advice.lower():
                    review_interval = "After 15 Days"
                elif "6 month" in advice.lower():
                    review_interval = "After 6 Months"
                elif "1 year" in advice.lower():
                    review_interval = "1 Year / Annual Checkup"
                    
                target_date = parse_relative_interval(review_interval, parse_relative_interval(reg_d_clean))
                if target_date is None:
                    target_date = datetime.now().date() + timedelta(days=30)
                    
                new_entry = {
                    "id": f"FU-{uuid.uuid4().hex[:10]}",
                    "patient_name": name,
                    "mobile": mobile,
                    "consultation_date": reg_d_clean,
                    "review_interval": review_interval,
                    "target_date": target_date.strftime("%Y-%m-%d") if target_date else "",
                    "diagnosis": issue,
                    "advice": advice,
                    "status": "Pending",
                    "reminders_count": 0,
                    "last_reminder_sent_at": "",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                data.append(new_entry)
                existing_keys.add(key)
                imported_count += 1
                
        if imported_count > 0:
            self._save_data(data)
            
        return imported_count

followup_manager = FollowupManager()

