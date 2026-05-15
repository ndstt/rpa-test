from typing import TypedDict
from datetime import datetime

class CourseDetail(TypedDict):
    url: str # use as primary key
    title: str
    category: str # Data, Design, Technology, Bussiness, AI
    cost: int # in THB
    overview: str
    instructor_name: str
    instructor_position: str # can be empty if the instructor are company or doesn't have position
    avg_rating: float # from 0 to 5
    total_reviews: int

class CourseReviewer(TypedDict):
    course_url: str # use as primary key
    name: str
    review_time: datetime
    review_text: str
    rating: float # from 0 to 5