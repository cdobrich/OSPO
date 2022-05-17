# This project makes use of PyGitHub. Install it by running:
#     pip install PyGithub

# Author: Clifton Dobrich

# NOTE: the functions get_pr_response_time() and get_issue_response_time() could ALMOST be generalized/templatized,
# except the method call for getting comments is slightly different for issues and pull-requests.

# NOTE: Attempts to use Github's API for get_issues(since=TIME) appears problematic.

from datetime import datetime, timedelta
from github import Github
from statistics import mean

DAYS_SINCE = 30
TIME_SINCE = (datetime.now() - timedelta(DAYS_SINCE))  # Get the time from 30-days ago

repositories = [
    'open-telemetry/opentelemetry-java',
    'open-telemetry/opentelemetry-java-contrib',
    'open-telemetry/opentelemetry.io',
    'open-telemetry/opentelemetry-collector',
    'open-telemetry/opentelemetry-specification',
]

GITHUB_TOKEN = "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"
g = Github(GITHUB_TOKEN)


def main(time_since=TIME_SINCE):
    """
    :param time_since: The datetime cut-off value for when pull requests are no longer considered.
                        Default value is 30 days.
    """
    datetime_time_deltas_total = []
    repository_average_response_time_in_seconds = {}
    for repoURL in repositories:
        datetime_time_deltas_individual = []
        print("INFO: Processing repo: ", repoURL)
        repo = g.get_repo(repoURL)

        # Get Issues
        issues = get_issues_since(repo, time_since)
        if len(issues) > 0:
            for issue in issues:
                time_to_response = get_issue_response_time(issue)
                if time_to_response is not None:
                    datetime_time_deltas_individual.append(time_to_response)

        # Get PRs
        pull_requests = get_pulls_since(repo, time_since)
        if len(pull_requests) > 0:
            for pr in pull_requests:
                time_to_response = get_pr_response_time(pr)
                if time_to_response is not None:
                    datetime_time_deltas_individual.append(time_to_response)

        repository_average_response_time_in_seconds[repoURL] = datetime_time_deltas_individual

    print("Calculation Reports for Repositories:")
    print("    Individual repository times")

    # Calculate average time of responses for each repository
    print()
    for repoName, values in repository_average_response_time_in_seconds.items():
        average_response_time_in_seconds = calculate_average_time(values)
        print_report(repoName, average_response_time_in_seconds)
        datetime_time_deltas_total.extend(values)

    # Calculate average total time of responses for all repositories
    # print()
    # print()
    # print("DEBUG:    Total list of response times: ", datetime_time_deltas_total)
    print()
    print()
    average_response_time_of_all_repositories_in_seconds = calculate_average_time(datetime_time_deltas_total)
    print_report("All Repositories: ", average_response_time_of_all_repositories_in_seconds)


def print_report(repository_name, average_response_time_in_seconds):
    """
    Print some potentially loggable, human-readable report information.
    """
    hours = average_response_time_in_seconds // 3600
    minutes = (average_response_time_in_seconds % 3600) // 60
    print("        '" + repository_name +
          "' average response time is {:02d} hours and {:02d} minutes".format(int(hours), int(minutes)))


def calculate_average_time(datetime_time_deltas):
    """
    Calculate average time of responses in seconds from input Datetime list.
    :returns: the mean (average) of the input list of Datetime objects.
    """
    time_deltas_values_in_seconds = []
    for value in datetime_time_deltas:  # Extract the time value from the Datetime objects
        time_deltas_values_in_seconds.append(value.total_seconds())
    return mean(time_deltas_values_in_seconds)


def get_issues_since(repository, since_time):
    """
    Get the Issues from input repository since the input time.
    :param repository: The target repository
    :param since_time: The datetime cut-off value for when pull requests are no longer considered.
    :returns: List of pull requests within the datetime range, or an empty list.
    """
    issues_within_valid_time_range = []
    issues_temp = repository.get_issues()
    for issue_candidate in issues_temp:
        if check_item_is_within_accepted_range(issue_candidate, since_time):
            issues_within_valid_time_range.append(issue_candidate)
    return issues_within_valid_time_range


def get_pulls_since(repository, since_time):
    """
    Get the Pull Requests from input repository since the input time.
    :param repository: The target repository
    :param since_time: The datetime cut-off value for when pull requests are no longer considered.
    :returns: List of pull requests within the datetime range, or an empty list.
    """
    pull_requests_within_valid_time_range = []
    pull_requests_temp = repository.get_pulls()
    for pr_candidate in pull_requests_temp:
        if check_item_is_within_accepted_range(pr_candidate, since_time):
            pull_requests_within_valid_time_range.append(pr_candidate)
    return pull_requests_within_valid_time_range


def check_item_is_within_accepted_range(item, since_time):
    """
    Determine if the input Issue/Pull Request object's created time is within (greater than) the input Datetime delta.

    :param item: The candidate issue (type Issue) or pull request (type Pull Request).
    :param since_time: The datetime cut-off value for when pull requests are no longer considered valid.
    :returns: True if within allowed time range, or False if not.
    """
    if item.created_at > since_time:
        return True
    else:
        return False


def get_pr_response_time(pull_request):
    """
    Get time since creation of PR and first non-bot response comment.
    :returns: None if nothing valid or Datetime of time difference.
    """
    print("INFO:    Processing Pull Request: ", pull_request.number)
    pull_request_created_at = pull_request.created_at
    comment_created_at = None
    for comment in pull_request.get_issue_comments():  # Assuming comments are in order
        if check_if_user_is_bot(comment.user.login):  # Only use comments from non-bots
            comment_created_at = comment.created_at
            break  # Stop at first valid non-bot response
    if comment_created_at is not None:
        # Found a valid comment from a non-bot
        time_delta = comment_created_at - pull_request_created_at
        print("INFO:      Time Delta: ", time_delta)
        return time_delta
    else:
        # print("No valid responses yet for PR: ", pull_request.number)
        return None


def get_issue_response_time(issue):
    """
    Get time since creation of issue and first non-bot response comment.
    :returns: None if nothing valid or Datetime of time difference.
    """
    print("INFO:    Processing Issue: ", issue.number)
    issue_created_at = issue.created_at
    comment_created_at = None
    for comment in issue.get_comments():  # Assuming comments are in order
        if check_if_user_is_bot(comment.user.login):
            comment_created_at = comment.created_at
            break  # Stop at first valid non-bot response
    if comment_created_at is not None:
        # Found a valid comment from a non-bot
        time_delta = comment_created_at - issue_created_at
        print("INFO:      Time Delta: ", time_delta)
        return time_delta
    else:
        # print("No valid responses yet for issue: ", issue.number)
        return None


def check_if_user_is_bot(username) -> bool:
    """
    Checking based on whether the user type is Bot or not.
    :returns: True if user type is not a "Bot", or False otherwise.
    """
    user = g.get_user(username)
    if user is not None and not g.get_user(username).type == "Bot":
        return True
    else:
        return False


if __name__ == "__main__":
    main()
