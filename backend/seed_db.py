"""
Database Seeder - Create sample data for development/testing
Run: python seed_db.py
"""

import uuid
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import (
    User, Role, Society, Complaint, ComplaintComment, ComplaintVote,
    ComplaintEvidence, Escalation, KarmaLog, Notification,
    ComplaintCategory, ComplaintStatus, ComplaintPriority, NotificationType
)


def seed_database():
    """Seed the database with sample data."""
    app = create_app('development')
    
    with app.app_context():
        print("🗑️  Clearing existing data...")
        # Clear all data
        Notification.query.delete()
        KarmaLog.query.delete()
        Escalation.query.delete()
        ComplaintComment.query.delete()
        ComplaintVote.query.delete()
        ComplaintEvidence.query.delete()
        Complaint.query.delete()
        User.query.delete()
        Society.query.delete()
        # Don't delete roles
        
        db.session.commit()
        
        print("🏢 Creating societies...")
        societies = [
            Society(
                name="Green Valley Apartments",
                address="123 Green Valley Road, Sector 15",
                city="Mumbai",
                state="Maharashtra",
                pincode="400001",
                total_flats=100,
                contact_email="secretary@greenvalley.com",
                contact_phone="9876543210",
                allow_anonymous_complaints=True
            ),
            Society(
                name="Sunrise Heights",
                address="456 Sunrise Boulevard",
                city="Pune",
                state="Maharashtra",
                pincode="411001",
                total_flats=75,
                contact_email="secretary@sunriseheights.com",
                contact_phone="9876543211"
            ),
            Society(
                name="Royal Gardens",
                address="789 Royal Road",
                city="Bangalore",
                state="Karnataka",
                pincode="560001",
                total_flats=120
            )
        ]
        
        for society in societies:
            db.session.add(society)
        db.session.commit()
        
        print("👥 Creating users...")
        
        # Get roles
        admin_role = Role.query.filter_by(name='admin').first()
        secretary_role = Role.query.filter_by(name='secretary').first()
        committee_role = Role.query.filter_by(name='committee_member').first()
        resident_role = Role.query.filter_by(name='resident').first()
        
        users_data = [
            # Green Valley Users
            {"email": "admin@padosipolitics.com", "full_name": "System Admin", "flat_number": "ADMIN", "wing": "Admin", "society_id": 1, "roles": [admin_role], "karma_score": 100},
            {"email": "secretary@greenvalley.com", "full_name": "Rajesh Sharma", "flat_number": "A-101", "wing": "A Wing", "society_id": 1, "roles": [secretary_role], "karma_score": 75},
            {"email": "committee1@greenvalley.com", "full_name": "Priya Patel", "flat_number": "A-201", "wing": "A Wing", "society_id": 1, "roles": [committee_role], "karma_score": 50},
            {"email": "resident1@greenvalley.com", "full_name": "Amit Kumar", "flat_number": "A-301", "wing": "A Wing", "society_id": 1, "roles": [resident_role], "karma_score": 25},
            {"email": "resident2@greenvalley.com", "full_name": "Sneha Reddy", "flat_number": "A-401", "wing": "A Wing", "society_id": 1, "roles": [resident_role], "karma_score": 30},
            {"email": "resident3@greenvalley.com", "full_name": "Vikram Singh", "flat_number": "B-101", "wing": "B Wing", "society_id": 1, "roles": [resident_role], "karma_score": -10},
            {"email": "resident4@greenvalley.com", "full_name": "Anita Desai", "flat_number": "B-201", "wing": "B Wing", "society_id": 1, "roles": [resident_role], "karma_score": 45},
            {"email": "resident5@greenvalley.com", "full_name": "Mohammed Ali", "flat_number": "B-301", "wing": "B Wing", "society_id": 1, "roles": [resident_role], "karma_score": 20},
            {"email": "resident6@greenvalley.com", "full_name": "Deepa Nair", "flat_number": "B-401", "wing": "B Wing", "society_id": 1, "roles": [resident_role], "karma_score": 35},
            {"email": "resident7@greenvalley.com", "full_name": "Suresh Menon", "flat_number": "C-101", "wing": "C Wing", "society_id": 1, "roles": [resident_role], "karma_score": 15},
            
            # Sunrise Heights Users
            {"email": "secretary@sunrise.com", "full_name": "Arun Joshi", "flat_number": "101", "wing": "Tower 1", "society_id": 2, "roles": [secretary_role], "karma_score": 60},
            {"email": "resident@sunrise.com", "full_name": "Kavita Iyer", "flat_number": "201", "wing": "Tower 1", "society_id": 2, "roles": [resident_role], "karma_score": 40},
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                password=generate_password_hash("password123"),
                full_name=user_data["full_name"],
                flat_number=user_data["flat_number"],
                wing=user_data["wing"],
                society_id=user_data["society_id"],
                phone="98765" + str(random.randint(10000, 99999)),
                karma_score=user_data["karma_score"],
                fs_uniquifier=str(uuid.uuid4()),
                active=True
            )
            for role in user_data["roles"]:
                user.roles.append(role)
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        print("📝 Creating complaints...")
        
        # Get users for creating complaints
        amit = User.query.filter_by(email="resident1@greenvalley.com").first()
        sneha = User.query.filter_by(email="resident2@greenvalley.com").first()
        vikram = User.query.filter_by(email="resident3@greenvalley.com").first()
        anita = User.query.filter_by(email="resident4@greenvalley.com").first()
        mohammed = User.query.filter_by(email="resident5@greenvalley.com").first()
        
        complaints_data = [
            {
                "title": "Loud music after 10 PM from B-101",
                "description": "The resident of B-101 has been playing extremely loud music after 10 PM for the past week. This is disturbing the entire B Wing. I have tried to talk to them but they don't listen. This happens almost every day and continues till midnight.",
                "category": ComplaintCategory.NOISE.value,
                "complainant": amit,
                "accused_flat": "B-101",
                "accused_user": vikram,
                "is_anonymous": False,
                "priority": ComplaintPriority.HIGH.value,
                "status": ComplaintStatus.OPEN.value,
                "support_count": 5
            },
            {
                "title": "Parking space dispute",
                "description": "Mr. Vikram from B-101 has been parking his second car in the visitor parking for over a month now. This is causing problems for actual visitors and other residents who have guests. Despite multiple requests, he refuses to move the vehicle.",
                "category": ComplaintCategory.PARKING.value,
                "complainant": sneha,
                "accused_flat": "B-101",
                "accused_user": vikram,
                "is_anonymous": False,
                "priority": ComplaintPriority.MEDIUM.value,
                "status": ComplaintStatus.IN_PROGRESS.value,
                "support_count": 8
            },
            {
                "title": "Dog barking all night",
                "description": "The dog in flat A-401 barks continuously throughout the night. This has been happening for the past 2 weeks and is affecting the sleep of residents in A Wing. Request the owner to take appropriate measures.",
                "category": ComplaintCategory.PET.value,
                "complainant": anita,
                "accused_flat": "A-401",
                "accused_user": sneha,
                "is_anonymous": True,
                "priority": ComplaintPriority.MEDIUM.value,
                "status": ComplaintStatus.ACKNOWLEDGED.value,
                "support_count": 3
            },
            {
                "title": "Water leakage from above flat",
                "description": "There is continuous water leakage from flat B-301 into my flat B-201. The bathroom ceiling is completely damaged and there's water dripping 24/7. This needs immediate attention as it's causing electrical hazards.",
                "category": ComplaintCategory.MAINTENANCE.value,
                "complainant": anita,
                "accused_flat": "B-301",
                "accused_user": mohammed,
                "is_anonymous": False,
                "priority": ComplaintPriority.CRITICAL.value,
                "status": ComplaintStatus.ESCALATED.value,
                "support_count": 12
            },
            {
                "title": "Garbage dumped in corridor",
                "description": "Someone from C Wing is regularly dumping garbage bags in the common corridor instead of the designated bin area. This is causing bad smell and attracting insects. Request CCTV footage review.",
                "category": ComplaintCategory.CLEANLINESS.value,
                "complainant": mohammed,
                "accused_flat": None,
                "accused_user": None,
                "is_anonymous": True,
                "priority": ComplaintPriority.LOW.value,
                "status": ComplaintStatus.OPEN.value,
                "support_count": 6
            },
            {
                "title": "Unauthorized construction on balcony",
                "description": "Flat B-401 has constructed an unauthorized extension on their balcony which is against society rules and may pose structural risks. Please investigate and take necessary action.",
                "category": ComplaintCategory.OTHER.value,
                "complainant": vikram,
                "accused_flat": "B-401",
                "accused_user": User.query.filter_by(flat_number="B-401").first(),
                "is_anonymous": False,
                "priority": ComplaintPriority.HIGH.value,
                "status": ComplaintStatus.RESOLVED.value,
                "support_count": 4
            },
            {
                "title": "Security guard sleeping on duty",
                "description": "I have observed multiple times that the night security guard (11 PM shift) is sleeping on duty. This is a serious security concern for all residents. Requesting management to take strict action.",
                "category": ComplaintCategory.SECURITY.value,
                "complainant": amit,
                "accused_flat": None,
                "accused_user": None,
                "is_anonymous": False,
                "priority": ComplaintPriority.HIGH.value,
                "status": ComplaintStatus.RESOLVED.value,
                "support_count": 15
            },
            {
                "title": "Water pressure issue in A Wing",
                "description": "For the past few days, the water pressure in A Wing has been extremely low, especially during morning hours (6-9 AM). This is affecting daily routines of all A Wing residents.",
                "category": ComplaintCategory.WATER.value,
                "complainant": sneha,
                "accused_flat": None,
                "accused_user": None,
                "is_anonymous": False,
                "priority": ComplaintPriority.MEDIUM.value,
                "status": ComplaintStatus.IN_PROGRESS.value,
                "support_count": 10
            }
        ]
        
        complaints = []
        for idx, data in enumerate(complaints_data):
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            complaint = Complaint(
                title=data["title"],
                description=data["description"],
                category=data["category"],
                complainant_id=data["complainant"].id,
                accused_flat=data["accused_flat"],
                accused_user_id=data["accused_user"].id if data["accused_user"] else None,
                society_id=1,  # Green Valley
                is_anonymous=data["is_anonymous"],
                priority=data["priority"],
                status=data["status"],
                support_count=data["support_count"],
                created_at=created_at,
                updated_at=created_at
            )
            if data["status"] == ComplaintStatus.RESOLVED.value:
                complaint.resolved_at = datetime.utcnow() - timedelta(days=random.randint(1, 5))
                complaint.resolution_note = "Issue has been addressed and resolved satisfactorily."
            complaints.append(complaint)
            db.session.add(complaint)
        
        db.session.commit()
        
        print("💬 Creating comments...")
        
        comments_data = [
            {"complaint_idx": 0, "user": amit, "text": "This has been going on for too long. We need strict action.", "is_anonymous": False},
            {"complaint_idx": 0, "user": sneha, "text": "I support this complaint. The noise is unbearable.", "is_anonymous": False},
            {"complaint_idx": 0, "user": User.query.filter_by(email="secretary@greenvalley.com").first(), "text": "We have noted the complaint and will speak to the concerned resident.", "is_anonymous": False},
            {"complaint_idx": 1, "user": anita, "text": "I had the same issue last month. Visitor parking should be for visitors only.", "is_anonymous": False},
            {"complaint_idx": 3, "user": User.query.filter_by(email="committee1@greenvalley.com").first(), "text": "Plumber has been dispatched. Expected resolution within 24 hours.", "is_anonymous": False},
            {"complaint_idx": 6, "user": vikram, "text": "I've seen this too. Very concerning for our safety.", "is_anonymous": True},
        ]
        
        for data in comments_data:
            comment = ComplaintComment(
                complaint_id=complaints[data["complaint_idx"]].id,
                user_id=data["user"].id,
                comment_text=data["text"],
                is_anonymous=data["is_anonymous"],
                is_official=data["user"].is_committee_member()
            )
            db.session.add(comment)
        
        db.session.commit()
        
        print("👍 Creating votes...")
        
        # Add some votes
        all_residents = User.query.filter(User.society_id == 1).all()
        for complaint in complaints[:5]:
            voters = random.sample(all_residents, min(len(all_residents), random.randint(3, 8)))
            for voter in voters:
                if voter.id != complaint.complainant_id:
                    vote = ComplaintVote(
                        complaint_id=complaint.id,
                        user_id=voter.id,
                        vote_type='support' if random.random() > 0.2 else 'oppose',
                        is_anonymous=random.random() > 0.5
                    )
                    db.session.add(vote)
        
        db.session.commit()
        
        print("⬆️ Creating escalations...")
        
        # Create escalation for the critical complaint
        escalation = Escalation(
            complaint_id=complaints[3].id,  # Water leakage complaint
            escalated_by_id=anita.id,
            escalated_to='secretary',
            reason='Complaint not addressed for 5 days despite critical priority. Water leakage causing electrical hazards.',
            previous_status=ComplaintStatus.ACKNOWLEDGED.value,
            is_auto_escalated=False,
            is_acknowledged=True,
            acknowledged_at=datetime.utcnow() - timedelta(days=1),
            response_note='Taken up on priority. Plumber dispatched.'
        )
        db.session.add(escalation)
        db.session.commit()
        
        print("🔔 Creating notifications...")
        
        for user in users[:5]:
            for i in range(random.randint(2, 5)):
                notification = Notification(
                    user_id=user.id,
                    title=random.choice([
                        'New complaint filed',
                        'Complaint status updated',
                        'Someone supported your complaint',
                        'New comment on complaint'
                    ]),
                    message='This is a sample notification message for testing purposes.',
                    notification_type=random.choice([
                        NotificationType.COMPLAINT,
                        NotificationType.VOTE,
                        NotificationType.COMMENT
                    ]),
                    is_read=random.random() > 0.5,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
                )
                db.session.add(notification)
        
        db.session.commit()
        
        print("\n✅ Database seeded successfully!")
        print("\n📊 Summary:")
        print(f"   Societies: {Society.query.count()}")
        print(f"   Users: {User.query.count()}")
        print(f"   Complaints: {Complaint.query.count()}")
        print(f"   Comments: {ComplaintComment.query.count()}")
        print(f"   Votes: {ComplaintVote.query.count()}")
        print(f"   Notifications: {Notification.query.count()}")
        
        print("\n🔑 Login Credentials:")
        print("   Admin: admin@padosipolitics.com / password123")
        print("   Secretary: secretary@greenvalley.com / password123")
        print("   Committee: committee1@greenvalley.com / password123")
        print("   Resident: resident1@greenvalley.com / password123")


if __name__ == '__main__':
    seed_database()
