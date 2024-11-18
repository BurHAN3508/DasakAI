from github import Github
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import base64
from datetime import datetime, timedelta

class GitHubManager:
    def __init__(self):
        """Initialize GitHub manager with API token"""
        load_dotenv()
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.user = self.github.get_user()
        
    def learn_from_github(self, topics: List[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """Learn from GitHub trending repositories and activities"""
        if topics is None:
            topics = ["python", "ai", "machine-learning", "artificial-intelligence"]
            
        learned_data = []
        
        # Get trending repositories
        query = f"stars:>100 created:>{(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')}"
        if topics:
            query += " " + " ".join(f"topic:{topic}" for topic in topics)
            
        trending_repos = self.github.search_repositories(query)
        
        for repo in trending_repos[:10]:  # Learn from top 10 trending repos
            repo_data = {
                "type": "trending_repository",
                "name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "topics": repo.get_topics(),
                "languages": repo.get_languages(),
                "readme": self._get_readme_content(repo)
            }
            learned_data.append(repo_data)
            
        return learned_data
        
    def _get_readme_content(self, repo) -> str:
        """Get README content from repository"""
        try:
            readme = repo.get_readme()
            content = base64.b64decode(readme.content).decode('utf-8')
            return content
        except:
            return ""
            
    def get_user_activity(self) -> Dict[str, Any]:
        """Get user's GitHub activity"""
        activity = {
            "repositories": self.list_repositories(),
            "starred_repos": self._get_starred_repos(),
            "contributions": self._get_contributions(),
            "following": self._get_following_activity()
        }
        return activity
        
    def _get_starred_repos(self) -> List[Dict[str, Any]]:
        """Get user's starred repositories"""
        return [{
            "name": repo.full_name,
            "description": repo.description,
            "topics": repo.get_topics()
        } for repo in self.user.get_starred()[:20]]
        
    def _get_contributions(self) -> List[Dict[str, Any]]:
        """Get user's recent contributions"""
        events = self.user.get_events()
        return [{
            "type": event.type,
            "repo": event.repo.name,
            "created_at": event.created_at.isoformat()
        } for event in events[:30]]
        
    def _get_following_activity(self) -> List[Dict[str, Any]]:
        """Get activity from users being followed"""
        following_events = []
        for following in self.user.get_following():
            events = following.get_events()
            following_events.extend([{
                "user": following.login,
                "type": event.type,
                "repo": event.repo.name,
                "created_at": event.created_at.isoformat()
            } for event in events[:5]])
        return following_events

    def analyze_repository(self, repo_name: str) -> Dict[str, Any]:
        """Detailed analysis of a repository"""
        try:
            repo = self.github.get_repo(repo_name)
            analysis = {
                "info": {
                    "name": repo.full_name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "topics": repo.get_topics(),
                    "languages": repo.get_languages()
                },
                "activity": {
                    "commits": self._analyze_commits(repo),
                    "issues": self._analyze_issues(repo),
                    "pull_requests": self._analyze_pull_requests(repo)
                },
                "community": {
                    "contributors": self._get_contributors(repo),
                    "readme": self._get_readme_content(repo),
                    "license": repo.get_license().license.name if repo.get_license() else None
                }
            }
            return analysis
        except Exception as e:
            return {"error": str(e)}

    def _analyze_commits(self, repo) -> List[Dict[str, Any]]:
        """Analyze recent commits"""
        commits = []
        for commit in repo.get_commits()[:20]:
            commits.append({
                "sha": commit.sha,
                "message": commit.commit.message,
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat()
            })
        return commits

    def _analyze_issues(self, repo) -> List[Dict[str, Any]]:
        """Analyze repository issues"""
        issues = []
        for issue in repo.get_issues(state='all')[:20]:
            issues.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "labels": [label.name for label in issue.labels],
                "created_at": issue.created_at.isoformat()
            })
        return issues

    def _analyze_pull_requests(self, repo) -> List[Dict[str, Any]]:
        """Analyze pull requests"""
        prs = []
        for pr in repo.get_pulls(state='all')[:20]:
            prs.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "labels": [label.name for label in pr.labels],
                "created_at": pr.created_at.isoformat()
            })
        return prs

    def _get_contributors(self, repo) -> List[Dict[str, Any]]:
        """Get repository contributors"""
        return [{
            "login": contributor.login,
            "contributions": contributor.contributions
        } for contributor in repo.get_contributors()[:20]]

    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private
            )
            return {
                "success": True,
                "repo_url": repo.html_url,
                "clone_url": repo.clone_url,
                "message": f"Successfully created repository: {repo.html_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create repository: {str(e)}"
            }

    def list_repositories(self) -> List[Dict[str, Any]]:
        """List all repositories for the authenticated user"""
        try:
            repos = self.user.get_repos()
            return [{
                "name": repo.name,
                "url": repo.html_url,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "topics": repo.get_topics(),
                "languages": repo.get_languages()
            } for repo in repos]
        except Exception as e:
            return []

    def create_issue(self, repo_name: str, title: str, body: str, labels: List[str] = None) -> Dict[str, Any]:
        """Create an issue in a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body, labels=labels)
            return {
                "success": True,
                "issue_url": issue.html_url,
                "message": f"Successfully created issue: {issue.html_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create issue: {str(e)}"
            }

    def create_pull_request(self, repo_name: str, title: str, body: str, 
                          head: str, base: str = "main", labels: List[str] = None) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            repo = self.user.get_repo(repo_name)
            pr = repo.create_pull(title=title, body=body, head=head, base=base)
            if labels:
                pr.add_to_labels(*labels)
            return {
                "success": True,
                "pr_url": pr.html_url,
                "message": f"Successfully created PR: {pr.html_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create PR: {str(e)}"
            }

    def search_code(self, query: str, language: str = None) -> List[Dict[str, Any]]:
        """Search for code across GitHub"""
        try:
            if language:
                query = f"{query} language:{language}"
            results = self.github.search_code(query)
            return [{
                "repository": code.repository.full_name,
                "path": code.path,
                "url": code.html_url,
                "score": code.score,
                "content": base64.b64decode(code.content).decode('utf-8')
            } for code in results[:10]]
        except Exception as e:
            return []

    def star_repository(self, repo_name: str) -> Dict[str, Any]:
        """Star a repository"""
        try:
            repo = self.github.get_repo(repo_name)
            repo.add_to_stargazers()
            return {
                "success": True,
                "message": f"Successfully starred repository: {repo.html_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to star repository: {str(e)}"
            }

    def fork_repository(self, repo_name: str) -> Dict[str, Any]:
        """Fork a repository"""
        try:
            repo = self.github.get_repo(repo_name)
            fork = self.user.create_fork(repo)
            return {
                "success": True,
                "fork_url": fork.html_url,
                "message": f"Successfully forked repository: {fork.html_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to fork repository: {str(e)}"
            }

    def watch_repository(self, repo_name: str) -> Dict[str, Any]:
        """Watch a repository"""
        try:
            repo = self.github.get_repo(repo_name)
            repo.subscribe()
            return {
                "success": True,
                "message": f"Successfully watching repository: {repo.html_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to watch repository: {str(e)}"
            }

    def create_gist(self, description: str, files: Dict[str, str], public: bool = False) -> Dict[str, Any]:
        """Create a GitHub Gist"""
        try:
            gist_files = {name: {'content': content} for name, content in files.items()}
            gist = self.github.get_user().create_gist(public, gist_files, description)
            return {
                "success": True,
                "gist_url": gist.html_url,
                "message": f"Successfully created gist: {gist.html_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create gist: {str(e)}"
            }
