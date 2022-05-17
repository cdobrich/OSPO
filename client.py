# NOTE: the functions get_pr_response_time() and get_issue_response_time() could ALMOST be generalized/templatized,
# except the method call for getting comments is slightly different for issues and pull-requests.

from datetime import datetime, timedelta
from github import Github
from statistics import mean

API_BASE_STRING = "https://api.github.com/repos/"
DAYS_SINCE = 30
TIME_SINCE = (datetime.now() - timedelta(DAYS_SINCE))  # Get the time from 30-days ago

repositories = [
    'open-telemetry/opentelemetry-java',
    'open-telemetry/opentelemetry-java-contrib',
    'open-telemetry/opentelemetry.io',
    'open-telemetry/opentelemetry-collector',
    'open-telemetry/opentelemetry-specification',
]

GITHUB_TOKEN = "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"  # Allow for more API requests
g = Github(GITHUB_TOKEN)  # No token required


def main():
    datetime_time_deltas = []
    for repoURL in repositories:
        repo = g.get_repo(repoURL)

        # Get Issues
        issues = repo.get_issues(since=TIME_SINCE)
        if issues.totalCount > 0:
            for issue in issues:
                time_to_response = get_issue_response_time(issue)
                if time_to_response is not None:
                    datetime_time_deltas.append(time_to_response)

        # Get PRs
        pull_requests = get_pulls_since(repo, TIME_SINCE)
        if len(pull_requests) > 0:
            for pr in pull_requests:
                time_to_response = get_pr_response_time(pr)
                if time_to_response is not None:
                    datetime_time_deltas.append(time_to_response)

    # Calculate average time of responses
    time_deltas_values_in_seconds = []
    for value in datetime_time_deltas:
        time_deltas_values_in_seconds.append(value.total_seconds())
    print()
    print("time_deltas_values_in_seconds: ", time_deltas_values_in_seconds)
    average_response_time_in_seconds = mean(time_deltas_values_in_seconds)
    print("average_response_time_in_seconds: ", average_response_time_in_seconds)
    hours = average_response_time_in_seconds // 3600
    minutes = (average_response_time_in_seconds % 3600) // 60
    print("The average response time is {:02d}:{:02d}".format(int(hours), int(minutes)))


def get_pulls_since(repository, since_time):
    """
    Get the Pull Requests from input repository since the input time.
    :param repository: The target repository
    :param since_time: The datetime cut-off value for when pull requests are no longer considered valid.
    :returns: List of pull requests within the datetime range, or an empty list.
    """
    pull_requests_within_valid_time_range = []
    pull_requests_temp = repository.get_pulls()
    for pr_candidate in pull_requests_temp:
        if check_pull_requests_is_within_accepted_range(pr_candidate, since_time):
            pull_requests_within_valid_time_range.append(pr_candidate)
    return pull_requests_within_valid_time_range


def check_pull_requests_is_within_accepted_range(pr, since_time):
    """
    Determine if the input Pull Request object's created time is within (greater than) the input Datetime delta.

    :param pr: The candidate pull request
    :param since_time: The datetime cut-off value for when pull requests are no longer considered valid.
    :returns: True if within allowed time range, or False if not.
    """
    if pr.created_at > since_time:
        return True
    else:
        return False


def get_pr_response_time(pull_request):
    """
    Get time since creation of PR and first non-bot response comment.
    :returns None if nothing valid or Datetime of time difference.
    """
    pull_request_created_at = pull_request.created_at
    comment_created_at = None
    for comment in pull_request.get_issue_comments():  # Assuming comments are in order
        if check_if_user_is_bot(comment.user.login):  # Only use comments from non-bots
            comment_created_at = comment.created_at
            break  # Stop at first valid non-bot response
    if comment_created_at is not None:
        # Found a valid comment from a non-bot
        time_diff = comment_created_at - pull_request_created_at
        print("Timediff: ", time_diff)
        return time_diff
    else:
        # print("No valid responses yet for PR: ", pull_request.number)
        return None


def get_issue_response_time(issue):
    """
    Get time since creation of issue and first non-bot response comment.
    :returns None if nothing valid or Datetime of time difference.
    """
    issue_created_at = issue.created_at
    comment_created_at = None
    for comment in issue.get_comments():  # Assuming comments are in order
        if check_if_user_is_bot(comment.user.login):
            comment_created_at = comment.created_at
            break  # Stop at first valid non-bot response
    if comment_created_at is not None:
        # Found a valid comment from a non-bot
        time_diff = comment_created_at - issue_created_at
        print("Timediff: ", time_diff)
        return time_diff
    else:
        # print("No valid responses yet for issue: ", issue.number)
        return None


def check_if_user_is_bot(username) -> bool:
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
