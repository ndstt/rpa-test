from typing import TypedDict
from datetime import datetime

class CourseDetail(TypedDict):
    url: str # use as primary key
    title: str
    cost: int # in THB
    overview: str
    instructor_name: str
    instructor_position: str # can be empty if the instructor are company or doesn't have position
    avg_rating: float # from 0 to 5
    total_reviews: int

class CourseCategory(TypedDict):
    course_url: str
    category: str