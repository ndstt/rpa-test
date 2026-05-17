from typing import TypedDict

class CourseDetail(TypedDict):
    url: str # use as primary key
    title: str
    cost: int # in THB
    overview: str
    instructor_name: str
    avg_rating: float # from 0 to 5
    total_reviews: int
    overall_satisfaction_percentage: int # from 0 to 100
    content_satisfaction_percentage : int # from 0 to 100
    instructor_satisfaction_percentage: int # from 0 to 100
    content_arrangement_satisfaction_percentage: int # from 0 to 100

class CourseCategory(TypedDict):
    course_url: str
    category: str

class InstructorDetail(TypedDict, total=False):
    name: str
    position: str # if any. the instructor can be institute or company