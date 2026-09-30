"""
Streamlit Web Dashboard for GitHub Activity & Repository Reporter.
Provides interactive web UI for Single User Analytics and Developer VS Mode Comparison.
"""

import os
import sys
import streamlit as st
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv

# Ensure `src` package is available on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.github_client import GitHubClient, GitHubAPIError
from src.analytics.statistics import GitHubAnalytics
from src.exporters.markdown_exporter import MarkdownExporter

load_dotenv()

# Streamlit Page Configuration
st.set_page_config(
    page_title="GitHub Activity & Repo Reporter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Navigation
st.sidebar.title("⚙️ Dashboard Controls")
mode = st.sidebar.radio(
    "Select Feature Mode:",
    ["Single Profile Analytics 📊", "Developer VS Mode ⚔️"]
)

token_input = st.sidebar.text_input(
    "GitHub Token (Optional)",
    type="password",
    help="Provide a PAT to increase GitHub API limit from 60 to 5,000 requests/hr."
)
token = token_input or os.getenv("GITHUB_TOKEN")
client = GitHubClient(token=token)

def fetch_user_data(username: str):
    profile = client.get_user_profile(username)
    repos = client.get_user_repos(username)
    events = client.get_user_events(username)

    repo_languages = []
    for repo in repos[:30]:
        langs_url = repo.get("languages_url")
        if langs_url:
            langs = client.get_repo_languages(langs_url)
            if langs:
                repo_languages.append(langs)

    repo_stats = GitHubAnalytics.process_repositories(repos)
    lang_stats = GitHubAnalytics.process_language_distribution(repo_languages)
    activity_stats = GitHubAnalytics.process_events(events)

    return {
        "profile": profile,
        "repo_stats": repo_stats,
        "language_stats": lang_stats,
        "activity_stats": activity_stats
    }


# ==========================================
# MODE 1: SINGLE PROFILE ANALYTICS
# ==========================================
if mode == "Single Profile Analytics 📊":
    st.sidebar.markdown("---")
    username_input = st.sidebar.text_input("GitHub Username", value="abinjoyal")
    generate_btn = st.sidebar.button("🔍 Generate Report", type="primary")

    st.title("📊 GitHub Activity & Repository Reporter")
    st.caption("Developer utility for REST API analytics, language statistics, and automated Markdown export.")

    username = username_input.strip()

    if generate_btn or username:
        if not username:
            st.warning("Please enter a valid GitHub username.")
        else:
            with st.spinner(f"Fetching GitHub REST API data for **{username}**..."):
                try:
                    data = fetch_user_data(username)
                    profile = data["profile"]
                    repo_stats = data["repo_stats"]
                    lang_stats = data["language_stats"]
                    activity_stats = data["activity_stats"]

                    # User Header Profile Card
                    col_avatar, col_info = st.columns([1, 4])
                    with col_avatar:
                        st.image(profile.get("avatar_url"), width=130)
                    with col_info:
                        st.subheader(f"{profile.get('name') or username} (@{username})")
                        st.markdown(f"**Bio:** {profile.get('bio') or 'N/A'}")
                        st.markdown(
                            f"📍 {profile.get('location') or 'N/A'} | "
                            f"🏢 {profile.get('company') or 'N/A'} | "
                            f"🔗 [{profile.get('html_url')}]({profile.get('html_url')})"
                        )

                    st.markdown("---")

                    # Metric Cards
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("Public Repos", repo_stats.get("total_repositories", 0))
                    m2.metric("Total Stars", repo_stats.get("total_stars", 0))
                    m3.metric("Total Forks", repo_stats.get("total_forks", 0))
                    m4.metric("Recent Commits", activity_stats.get("commits", 0))
                    m5.metric("Recent PRs", activity_stats.get("pull_requests", 0))

                    st.markdown("---")

                    left_chart, right_activity = st.columns([3, 2])

                    with left_chart:
                        st.subheader("🧑‍💻 Programming Language Share")
                        if lang_stats:
                            df_lang = pd.DataFrame(lang_stats, columns=["Language", "Percentage", "Bytes"])
                            fig_pie = px.pie(
                                df_lang, names="Language", values="Percentage", hole=0.4,
                                color_discrete_sequence=px.colors.qualitative.Pastel
                            )
                            fig_pie.update_traces(textinfo="percent+label")
                            st.plotly_chart(fig_pie, use_container_width=True)
                        else:
                            st.info("No public language data available for this user's repositories.")

                    with right_activity:
                        st.subheader("⚡ Recent Activity (Events)")
                        act_data = {
                            "Activity": ["Commits", "Pull Requests", "Issues", "Stars Given", "Created Repos"],
                            "Count": [
                                activity_stats.get("commits", 0),
                                activity_stats.get("pull_requests", 0),
                                activity_stats.get("issues", 0),
                                activity_stats.get("stars_given", 0),
                                activity_stats.get("repositories_created", 0),
                            ]
                        }
                        df_act = pd.DataFrame(act_data)
                        fig_bar = px.bar(
                            df_act, x="Activity", y="Count", color="Activity",
                            color_discrete_sequence=px.colors.qualitative.Safe
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)

                    st.markdown("---")

                    # Top Repositories Section
                    st.subheader("⭐ Top Repositories")
                    top_repos = repo_stats.get("top_starred_repos", [])
                    if top_repos:
                        df_repos = pd.DataFrame(top_repos)[["name", "language", "stars", "forks", "description", "html_url"]]
                        df_repos.columns = ["Repository Name", "Language", "Stars", "Forks", "Description", "URL"]
                        st.dataframe(df_repos, use_container_width=True)
                    else:
                        st.info("No repositories found.")

                    st.markdown("---")

                    # Report File Compiler & Download Button
                    st.subheader("📄 Report Export")

                    report_filepath = os.path.join("reports", f"{username}-report.md")
                    MarkdownExporter.generate_report(
                        profile=profile,
                        repo_stats=repo_stats,
                        language_stats=lang_stats,
                        activity_stats=activity_stats,
                        output_filepath=report_filepath
                    )

                    with open(report_filepath, "r", encoding="utf-8") as f:
                        md_content = f.read()

                    tab_preview, tab_download = st.tabs(["Preview Markdown Report", "Download Options"])
                    with tab_preview:
                        st.markdown(md_content)
                    with tab_download:
                        report_basename = os.path.basename(report_filepath)
                        st.download_button(
                            label=f"📥 Download {report_basename}",
                            data=md_content,
                            file_name=report_basename,
                            mime="text/markdown",
                            type="primary"
                        )

                except GitHubAPIError as err:
                    st.error(f"GitHub API Error: {err}")
                except Exception as err:
                    st.error(f"Unexpected Error: {err}")


# ==========================================
# MODE 2: DEVELOPER VS MODE ⚔️
# ==========================================
elif mode == "Developer VS Mode ⚔️":
    st.sidebar.markdown("---")
    u1_input = st.sidebar.text_input("User 1 Username", value="abinjoyal")
    u2_input = st.sidebar.text_input("User 2 Username", value="joyaldev363")
    vs_btn = st.sidebar.button("⚔️ Start Developer Match", type="primary")

    st.title("⚔️ Developer VS Mode - Side-by-Side Match")
    st.caption("Compare two GitHub profiles in real-time across repositories, stars, commits, and activity.")

    u1 = u1_input.strip()
    u2 = u2_input.strip()

    if vs_btn or (u1 and u2):
        if not u1 or not u2:
            st.warning("Please enter two GitHub usernames to compare.")
        else:
            with st.spinner(f"Comparing **@{u1}** vs **@{u2}**..."):
                try:
                    u1_data = fetch_user_data(u1)
                    u2_data = fetch_user_data(u2)

                    comp_res = GitHubAnalytics.compare_users(u1_data, u2_data)

                    # Match Winner Header Banner
                    st.success(f"### {comp_res['overall_winner']} (Score: @{u1} {comp_res['user1_score']} - {comp_res['user2_score']} @{u2})")

                    st.markdown("---")

                    # Side-by-Side Profile Headers
                    col1, col_vs, col2 = st.columns([4, 1, 4])

                    with col1:
                        p1 = u1_data["profile"]
                        st.image(p1.get("avatar_url"), width=110)
                        st.subheader(f"{p1.get('name') or u1} (@{u1})")
                        st.markdown(f"**Bio:** {p1.get('bio') or 'N/A'}")

                    with col_vs:
                        st.markdown("<h1 style='text-align: center;'>VS</h1>", unsafe_allow_html=True)

                    with col2:
                        p2 = u2_data["profile"]
                        st.image(p2.get("avatar_url"), width=110)
                        st.subheader(f"{p2.get('name') or u2} (@{u2})")
                        st.markdown(f"**Bio:** {p2.get('bio') or 'N/A'}")

                    st.markdown("---")

                    # Metric Comparison Table
                    st.subheader("📊 Metric Comparison Table")
                    df_comp = pd.DataFrame(comp_res["metrics"])
                    df_comp.columns = ["Metric", f"@{u1}", f"@{u2}", "Advantage Winner"]
                    st.dataframe(df_comp, use_container_width=True)

                    st.markdown("---")

                    # Comparative Plotly Bar Chart
                    st.subheader("📈 Comparative Chart")
                    chart_records = []
                    for m in comp_res["metrics"]:
                        chart_records.append({"Metric": m["metric"], "Value": m["val1"], "User": f"@{u1}"})
                        chart_records.append({"Metric": m["metric"], "Value": m["val2"], "User": f"@{u2}"})

                    df_chart = pd.DataFrame(chart_records)
                    fig_vs = px.bar(
                        df_chart,
                        x="Metric",
                        y="Value",
                        color="User",
                        barmode="group",
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    st.plotly_chart(fig_vs, use_container_width=True)

                    st.markdown("---")

                    # VS Report Export
                    st.subheader("📄 Export VS Report")
                    vs_report_filepath = os.path.join("reports", f"vs-{u1}-vs-{u2}.md")
                    MarkdownExporter.generate_comparison_report(
                        user1_data=u1_data,
                        user2_data=user2_data,
                        comp_res=comp_res,
                        output_filepath=vs_report_filepath
                    )

                    with open(vs_report_filepath, "r", encoding="utf-8") as f:
                        vs_md_content = f.read()

                    st.download_button(
                        label=f"📥 Download {os.path.basename(vs_report_filepath)}",
                        data=vs_md_content,
                        file_name=os.path.basename(vs_report_filepath),
                        mime="text/markdown",
                        type="primary"
                    )

                except GitHubAPIError as err:
                    st.error(f"GitHub API Error: {err}")
                except Exception as err:
                    st.error(f"Unexpected Error: {err}")
