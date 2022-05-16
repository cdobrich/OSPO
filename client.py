from datetime import datetime, timedelta

from github import Github
from pprint import pprint

API_BASE_STRING = "https://api.github.com/repos/"
DAYS_SINCE = 30
TIME_SINCE = (datetime.now() - timedelta(DAYS_SINCE))  # Get the time from 30-days ago

repos = [
    'open-telemetry/opentelemetry-java',
    'open-telemetry/opentelemetry-java-contrib',
    'open-telemetry/opentelemetry.io',
    'open-telemetry/opentelemetry-collector',
    'open-telemetry/opentelemetry-specification',
]

GITHUB_TOKEN = "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"  # Allow for more API requests
g = Github(GITHUB_TOKEN)  # No token required


def main():
    repo = g.get_repo(repos[0])

    # Get Issues
    issues = repo.get_issues(since=TIME_SINCE)
    # for issue in issues:
    issue = repo.get_issue(4448)
    print("Issue ID#: ", issue.number)
    print("  Number of comments: ", issue.comments)
    issue_created_at = issue.created_at
    comment_created_at = None
    for comment in issue.get_comments():  # Assuming comments are in order
        if checkIfUserIsBot(comment.user.login):
            comment_created_at = comment.created_at
            break
    if comment_created_at is not None:
        # Found a valid comment from a non-bot
        # print("Type: ", issue_created_at)
        timediff = comment_created_at - issue_created_at
        print("Timediff: ", timediff)
    else:
        print("No valid responses yet for issue: ", issue.id)

    # Get PRs
    # pr = repo.get_pull(1)
    # comments = pr.get_issue_comments()
    # for comment in comments:
    #     pass


def checkIfUserIsBot(username) -> bool:
    """
    Checking based on whether the user type is Bot or not.
    """
    user = g.get_user(username)
    if user is not None and not g.get_user(username).type == "Bot":
        return True
    else:
        return False


if __name__ == "__main__":
    main()
