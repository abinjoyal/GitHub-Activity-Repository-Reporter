"""
Streamlit Web Dashboard for GitHub Activity & Repository Reporter.
Provides an interactive web UI with metric cards, visual charts, and report exports.
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

# Sidebar Configuration
st.sidebar.title("⚙️ Configuration")
st.sidebar.markdown("Generate interactive reports for any public GitHub account.")

default_user = "abinjoyal"
username_input = st.sidebar.text_input("GitHub Username", value=default_user)
token_input = st.sidebar.text_input(
    "GitHub Token (Optional)",
    type="password",
    help="Provide a PAT to increase GitHub API limit from 60 to 5,000 requests/hr."
)

generate_btn = st.sidebar.button("🔍 Generate Report", type="primary")

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tip**: Leave the token field blank if you are fetching smaller public accounts."
)

# Header Section
st.title("📊 GitHub Activity & Repository Reporter")
st.caption("Developer utility for REST API analytics, language statistics, and automated Markdown export.")

username = username_input.strip()

if generate_btn or username:
    if not username:
        st.warning("Please enter a valid GitHub username.")
    else:
        with st.spinner(f"Fetching GitHub REST API data for **{username}**..."):
            token = token_input or os.getenv("GITHUB_TOKEN")
            client = GitHubClient(token=token)

            try:
                profile = client.get_user_profile(username)
                repos = client.get_user_repos(username)
                events = client.get_user_events(username)

                # Fetch language data for up to 30 recent repos
                repo_languages = []
                for repo in repos[:30]:
                    langs_url = repo.get("languages_url")
                    if langs_url:
                        langs = client.get_repo_languages(langs_url)
                        if langs:
                            repo_languages.append(langs)

                # Analytics processing
                repo_stats = GitHubAnalytics.process_repositories(repos)
                lang_stats = GitHubAnalytics.process_language_distribution(repo_languages)
                activity_stats = GitHubAnalytics.process_events(events)

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

                # Executive Metric Cards
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Public Repos", repo_stats.get("total_repositories", 0))
                m2.metric("Total Stars", repo_stats.get("total_stars", 0))
                m3.metric("Total Forks", repo_stats.get("total_forks", 0))
                m4.metric("Recent Commits", activity_stats.get("commits", 0))
                m5.metric("Recent PRs", activity_stats.get("pull_requests", 0))

                st.markdown("---")

                # Layout: Charts & Breakdown
                left_chart, right_activity = st.columns([3, 2])

                with left_chart:
                    st.subheader("🧑‍💻 Programming Language Share")
                    if lang_stats:
                        df_lang = pd.DataFrame(
                            lang_stats, columns=["Language", "Percentage", "Bytes"]
                        )
                        fig_pie = px.pie(
                            df_lang,
                            names="Language",
                            values="Percentage",
                            hole=0.4,
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
                        df_act,
                        x="Activity",
                        y="Count",
                        color="Activity",
                        color_discrete_sequence=px.colors.qualitative.Safe
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                st.markdown("---")

                # Top Starred Repositories Section
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
else:
    st.info("Enter a GitHub username in the left sidebar and click **Generate Report**.")
