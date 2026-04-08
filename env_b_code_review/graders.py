# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_b_code_review\graders.py
import ast
import re

class BugDetectionGrader:
    def score(self, action: dict, ground_truth: dict) -> float:
        score = 0.0
        try:
            if action.get("bug_line") == ground_truth.get("bug_line"):
                score += 0.4
            if action.get("bug_type") == ground_truth.get("bug_type"):
                score += 0.3
            
            # Check if fixed code is valid python
            if "fixed_code" in action:
                try:
                    ast.parse(action["fixed_code"])
                    # A more robust check would involve running tests against the fixed code
                    if "len(arr) - 1" in action["fixed_code"]: # Simple check for this specific bug
                        score += 0.3
                except (SyntaxError, TypeError):
                    pass # Invalid code gets 0 points for this part
        except Exception:
            return 0.0 # Should not happen with valid inputs
            
        return min(score, 1.0)

class SecurityReviewGrader:
    def score(self, action: dict, ground_truth: dict) -> float:
        try:
            if "vulnerabilities" not in action or not isinstance(action["vulnerabilities"], list):
                return 0.0

            ground_truth_vulns = {v['type']: v for v in ground_truth['vulnerabilities']}
            action_vulns = {v.get('type'): v for v in action['vulnerabilities']}
            
            total_planted_vulns = len(ground_truth_vulns)
            if total_planted_vulns == 0: return 1.0

            per_vuln_score = 1.0 / total_planted_vulns
            score = 0.0

            for vuln_type, gt_vuln in ground_truth_vulns.items():
                if vuln_type in action_vulns:
                    score += per_vuln_score
                    action_vuln = action_vulns[vuln_type]
                    if action_vuln.get('severity') == gt_vuln.get('severity'):
                        score += 0.1 # Bonus for correct severity
            
            return min(score, 1.0)
        except Exception:
            return 0.0

class FullPRReviewGrader:
    def score(self, action: dict, ground_truth: dict) -> float:
        try:
            weights = {
              "issues_identified": 0.40,
              "severity_accuracy": 0.30,
              "suggestion_quality": 0.30
            }
            
            # Score issues identified
            gt_issues = {f"{i['file']}-{i['line']}": i for i in ground_truth['issues']}
            action_issues = {f"{i.get('file')}-{i.get('line')}": i for i in action.get('issues', [])}
            
            found_count = len(set(gt_issues.keys()) & set(action_issues.keys()))
            issues_score = (found_count / len(gt_issues)) if gt_issues else 1.0
            
            # Score severity and suggestion
            severity_score = 0.0
            suggestion_score = 0.0
            if found_count > 0:
                correct_severity = 0
                correct_suggestion = 0
                for key, gt_issue in gt_issues.items():
                    if key in action_issues:
                        action_issue = action_issues[key]
                        if action_issue.get('severity') == gt_issue.get('severity'):
                            correct_severity += 1
                        # Simple keyword match for suggestion quality
                        if gt_issue.get('suggestion', '').split(' ')[0] in action_issue.get('suggestion', ''):
                            correct_suggestion += 1
                severity_score = correct_severity / found_count
                suggestion_score = correct_suggestion / found_count

            total_score = (weights['issues_identified'] * issues_score +
                           weights['severity_accuracy'] * severity_score +
                           weights['suggestion_quality'] * suggestion_score)

            return min(total_score, 1.0)
        except Exception:
            return 0.0
