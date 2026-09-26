import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="Instructor Performance and Course Quality Evaluation on EduPro",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------
# PROFESSIONAL / COLOURFUL CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #173b7a;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 17px;
    margin-bottom: 25px;
}

.kpi-card {
    padding: 20px;
    border-radius: 15px;
    background: white;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    text-align: center;
    border-top: 5px solid #4f46e5;
}

.kpi-title {
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}

.kpi-value {
    color: #172554;
    font-size: 28px;
    font-weight: 800;
    margin-top: 7px;
}

.section-title {
    color: #173b7a;
    font-size: 25px;
    font-weight: 750;
    margin-top: 30px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# MAIN PROJECT TITLE
# ---------------------------------------------------

st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #173b7a, #4f46e5);
        padding: 25px 20px;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0px 5px 18px rgba(0,0,0,0.15);
    ">
        <h1 style="
            color: white;
            font-size: 36px;
            font-weight: 800;
            margin: 0;
            line-height: 1.3;
        ">
            🎓 Instructor Performance and<br>
            Course Quality Evaluation on EduPro
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="
        text-align: center;
        color: #64748b;
        font-size: 17px;
        font-weight: 600;
        margin-bottom: 25px;
    ">
        Data-Driven Evaluation of Instructor Effectiveness and Course Quality
    </p>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------
# LOAD EXCEL DATA
# ---------------------------------------------------

FILE_NAME = "EduPro Online Platform.xlsx"

try:
    teachers = pd.read_excel(FILE_NAME, sheet_name="Teachers")
    courses = pd.read_excel(FILE_NAME, sheet_name="Courses")
    transactions = pd.read_excel(FILE_NAME, sheet_name="Transactions")

except Exception as e:
    st.error(
        "Excel file could not be loaded. Please check the Excel filename "
        "and sheet names: Teachers, Courses, Transactions."
    )
    st.stop()


# ---------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------

teachers = teachers.drop_duplicates(subset=["TeacherID"])
courses = courses.drop_duplicates(subset=["CourseID"])
transactions = transactions.drop_duplicates(subset=["TransactionID"])

teachers["TeacherRating"] = pd.to_numeric(
    teachers["TeacherRating"], errors="coerce"
)

teachers["YearsOfExperience"] = pd.to_numeric(
    teachers["YearsOfExperience"], errors="coerce"
)

courses["CourseRating"] = pd.to_numeric(
    courses["CourseRating"], errors="coerce"
)


# ---------------------------------------------------
# DATA INTEGRATION
# ---------------------------------------------------

course_teacher = courses.merge(
    transactions[["CourseID", "TeacherID"]].drop_duplicates(),
    on="CourseID",
    how="left"
)

course_teacher = course_teacher.merge(
    teachers[
        [
            "TeacherID",
            "TeacherName",
            "Age",
            "Gender",
            "Expertise",
            "YearsOfExperience",
            "TeacherRating"
        ]
    ],
    on="TeacherID",
    how="left"
)


# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("🎛️ Dashboard Filters")

expertise_options = sorted(
    course_teacher["Expertise"].dropna().unique().tolist()
)

category_options = sorted(
    course_teacher["CourseCategory"].dropna().unique().tolist()
)

level_options = sorted(
    course_teacher["CourseLevel"].dropna().unique().tolist()
)

selected_expertise = st.sidebar.multiselect(
    "Instructor Expertise",
    expertise_options,
    default=expertise_options
)

selected_category = st.sidebar.multiselect(
    "Course Category",
    category_options,
    default=category_options
)

selected_level = st.sidebar.multiselect(
    "Course Level",
    level_options,
    default=level_options
)

rating_min = float(courses["CourseRating"].min())
rating_max = float(courses["CourseRating"].max())

selected_rating = st.sidebar.slider(
    "Course Rating Range",
    min_value=rating_min,
    max_value=rating_max,
    value=(rating_min, rating_max),
    step=0.1
)


# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered_data = course_teacher[
    course_teacher["Expertise"].isin(selected_expertise)
    & course_teacher["CourseCategory"].isin(selected_category)
    & course_teacher["CourseLevel"].isin(selected_level)
    & course_teacher["CourseRating"].between(
        selected_rating[0],
        selected_rating[1]
    )
].copy()


# ---------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------

average_teacher_rating = teachers["TeacherRating"].mean()

average_course_rating = courses["CourseRating"].mean()

rating_consistency_index = (
    1 - (
        teachers["TeacherRating"].std()
        / teachers["TeacherRating"].mean()
    )
)

experience_impact_score = teachers["YearsOfExperience"].corr(
    teachers["TeacherRating"]
)

high_rated_teachers = teachers.loc[
    teachers["TeacherRating"] >= 4,
    "TeacherID"
]

high_rated_enrollments = transactions[
    transactions["TeacherID"].isin(high_rated_teachers)
]["TransactionID"].nunique()

total_enrollments = transactions["TransactionID"].nunique()

enrollment_influence_ratio = (
    high_rated_enrollments / total_enrollments
)


# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Key Performance Indicators</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Teacher Rating</div>
            <div class="kpi-value">{average_teacher_rating:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Course Rating</div>
            <div class="kpi-value">{average_course_rating:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Rating Consistency Index</div>
            <div class="kpi-value">{rating_consistency_index:.3f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Experience Impact Score</div>
            <div class="kpi-value">{experience_impact_score:.3f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Enrollment Influence Ratio</div>
            <div class="kpi-value">{enrollment_influence_ratio:.3f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------
# INSTRUCTOR PERFORMANCE LEADERBOARD
# ---------------------------------------------------

st.markdown(
    '<div class="section-title">🏆 Instructor Performance Leaderboard</div>',
    unsafe_allow_html=True
)

teacher_enrollments = (
    transactions.groupby("TeacherID")["TransactionID"]
    .nunique()
    .reset_index(name="Enrollments")
)

leaderboard = teachers.merge(
    teacher_enrollments,
    on="TeacherID",
    how="left"
)

leaderboard["Enrollments"] = leaderboard["Enrollments"].fillna(0)

leaderboard = leaderboard[
    leaderboard["Expertise"].isin(selected_expertise)
]

leaderboard = leaderboard.sort_values(
    "TeacherRating",
    ascending=False
)

st.dataframe(
    leaderboard[
        [
            "TeacherName",
            "Expertise",
            "YearsOfExperience",
            "TeacherRating",
            "Enrollments"
        ]
    ].reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------
# EXPERIENCE VS RATING
# ---------------------------------------------------

st.markdown(
    '<div class="section-title">📈 Experience vs Instructor Performance</div>',
    unsafe_allow_html=True
)

experience_data = teachers[
    teachers["Expertise"].isin(selected_expertise)
].copy()

fig_experience_teacher = px.scatter(
    experience_data,
    x="YearsOfExperience",
    y="TeacherRating",
    color="Expertise",
    hover_name="TeacherName",
    size="TeacherRating",
    title="Years of Experience vs Teacher Rating",
    labels={
        "YearsOfExperience": "Years of Experience",
        "TeacherRating": "Teacher Rating"
    },
    template="plotly_white"
)

fig_experience_teacher.update_layout(
    height=500
)

st.plotly_chart(
    fig_experience_teacher,
    use_container_width=True
)


# ---------------------------------------------------
# EXPERIENCE VS COURSE RATING
# ---------------------------------------------------

experience_course = course_teacher[
    course_teacher["Expertise"].isin(selected_expertise)
].copy()

fig_experience_course = px.scatter(
    experience_course,
    x="YearsOfExperience",
    y="CourseRating",
    color="Expertise",
    hover_name="CourseName",
    size="CourseRating",
    title="Years of Experience vs Course Rating",
    labels={
        "YearsOfExperience": "Years of Experience",
        "CourseRating": "Course Rating"
    },
    template="plotly_white"
)

fig_experience_course.update_layout(
    height=500
)

st.plotly_chart(
    fig_experience_course,
    use_container_width=True
)


# ---------------------------------------------------
# COURSE QUALITY HEATMAP
# ---------------------------------------------------

st.markdown(
    '<div class="section-title">🔥 Course Quality Heatmap</div>',
    unsafe_allow_html=True
)

heatmap_data = filtered_data.pivot_table(
    index="CourseCategory",
    columns="CourseLevel",
    values="CourseRating",
    aggfunc="mean"
)

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto=".2f",
    aspect="auto",
    title="Average Course Rating by Category and Level",
    labels={
        "x": "Course Level",
        "y": "Course Category",
        "color": "Course Rating"
    },
    color_continuous_scale="RdYlGn"
)

fig_heatmap.update_layout(
    height=550
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)


# ---------------------------------------------------
# EXPERTISE-WISE PERFORMANCE
# ---------------------------------------------------

st.markdown(
    '<div class="section-title">📚 Expertise-wise Performance Comparison</div>',
    unsafe_allow_html=True
)

expertise_performance = (
    filtered_data.groupby("Expertise")
    .agg(
        Average_Teacher_Rating=("TeacherRating", "mean"),
        Average_Course_Rating=("CourseRating", "mean"),
        Courses=("CourseID", "nunique")
    )
    .reset_index()
)

expertise_long = expertise_performance.melt(
    id_vars="Expertise",
    value_vars=[
        "Average_Teacher_Rating",
        "Average_Course_Rating"
    ],
    var_name="Metric",
    value_name="Rating"
)

fig_expertise = px.bar(
    expertise_long,
    x="Expertise",
    y="Rating",
    color="Metric",
    barmode="group",
    title="Teacher Rating vs Course Rating by Expertise",
    template="plotly_white"
)

fig_expertise.update_layout(
    height=500,
    xaxis_tickangle=-35
)

st.plotly_chart(
    fig_expertise,
    use_container_width=True
)
# ---------------------------------------------------
# INSTRUCTOR RATING TIER ANALYSIS
# ---------------------------------------------------

st.markdown(
    '<div class="section-title">⭐ Instructor Rating Tier Analysis</div>',
    unsafe_allow_html=True
)

# Create rating tiers
tier_data = teachers.copy()

tier_data["Rating_Tier"] = pd.cut(
    tier_data["TeacherRating"],
    bins=[-float("inf"), 3, 4, float("inf")],
    labels=["Low Rated", "Mid Rated", "High Rated"],
    right=False
)

# Course rating by instructor rating tier
tier_course_data = course_teacher.merge(
    tier_data[["TeacherID", "Rating_Tier"]],
    on="TeacherID",
    how="left"
)

tier_summary = (
    tier_course_data.groupby("Rating_Tier", observed=True)
    .agg(
        Average_Course_Rating=("CourseRating", "mean"),
        Courses=("CourseID", "nunique")
    )
    .reset_index()
)

# Enrollment count by rating tier
tier_enrollment = transactions.merge(
    tier_data[["TeacherID", "Rating_Tier"]],
    on="TeacherID",
    how="left"
)

enrollment_summary = (
    tier_enrollment.groupby("Rating_Tier", observed=True)
    .agg(
        Enrollments=("TransactionID", "nunique")
    )
    .reset_index()
)

# Combine both summaries
tier_summary = tier_summary.merge(
    enrollment_summary,
    on="Rating_Tier",
    how="left"
)

# Display table
st.dataframe(
    tier_summary,
    use_container_width=True,
    hide_index=True
)

# Course Rating comparison
fig_tier_course = px.bar(
    tier_summary,
    x="Rating_Tier",
    y="Average_Course_Rating",
    title="Average Course Rating by Instructor Rating Tier",
    text_auto=".2f",
    template="plotly_white"
)

fig_tier_course.update_layout(
    height=450,
    xaxis_title="Instructor Rating Tier",
    yaxis_title="Average Course Rating"
)

st.plotly_chart(
    fig_tier_course,
    use_container_width=True
)

# Enrollment comparison
fig_tier_enrollment = px.bar(
    tier_summary,
    x="Rating_Tier",
    y="Enrollments",
    title="Enrollment Volume by Instructor Rating Tier",
    text_auto=True,
    template="plotly_white"
)

fig_tier_enrollment.update_layout(
    height=450,
    xaxis_title="Instructor Rating Tier",
    yaxis_title="Number of Enrollments"
)

st.plotly_chart(
    fig_tier_enrollment,
    use_container_width=True
)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#64748b;">
        🎓 EduPro Instructor Performance & Course Quality Evaluation
        <br>
        Data Science  Project
        <br><br>
        <b>Created by Durga Prasad Annamdevula</b>
    </div>
    """,
    unsafe_allow_html=True
)
