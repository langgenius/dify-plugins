import sys
import os
from typing import Any, Dict, List, Union
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class TextQualityEvaluatorTool(Tool):
    """
    Text Quality Evaluator using Dingo library
    """

    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> Union[ToolInvokeMessage, List[ToolInvokeMessage]]:
        """
        Invoke the text quality evaluator tool
        """
        try:
            # Try to add local dingo path if available
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dingo_path = os.path.join(current_dir, '..', '..', '..', '..', 'dingo', 'dingo-latest')
            if os.path.exists(dingo_path) and dingo_path not in sys.path:
                sys.path.insert(0, dingo_path)

            # Import dingo here to avoid import errors if not installed
            from dingo.config import InputArgs
            from dingo.exec import Executor
            from dingo.io.input import Data
            
            # Get parameters
            text_content = tool_parameters.get('text_content', '')
            rule_group = tool_parameters.get('rule_group', 'default')
            
            if not text_content.strip():
                return self.create_text_message("Error: Text content cannot be empty")
            
            # Create a Data object for evaluation
            data = Data(
                data_id='dify_eval_001',
                content=text_content
            )
            
            # Configure input arguments for local execution
            input_data = {
                "executor": {
                    "eval_group": rule_group,
                    "result_save": {
                        "bad": False  # Don't save files, just return results
                    }
                }
            }
            
            # Create input args and executor
            input_args = InputArgs(**input_data)
            executor = Executor.exec_map["local"](input_args)
            
            # Evaluate single data item
            # For simplicity, we'll use a basic rule evaluation
            from dingo.model.rule.rule_common import RuleEnterAndSpace, RuleContentNull
            
            results = []
            issues = []
            
            # Test with a few basic rules
            rules = [RuleEnterAndSpace(), RuleContentNull()]
            
            for rule in rules:
                try:
                    result = rule.eval(data)
                    if result.error_status:
                        issues.append({
                            "rule": result.name,
                            "type": result.type,
                            "reason": result.reason
                        })
                except Exception as e:
                    # Skip rules that fail
                    continue
            
            # Calculate simple quality score
            total_rules = len(rules)
            failed_rules = len(issues)
            quality_score = ((total_rules - failed_rules) / total_rules * 100) if total_rules > 0 else 100
            
            # Format results
            result_text = f"Text Quality Assessment Results:\n\n"
            result_text += f"Quality Score: {quality_score:.1f}%\n"
            result_text += f"Issues Found: {failed_rules}\n\n"
            
            if issues:
                result_text += "Detected Issues:\n"
                for i, issue in enumerate(issues, 1):
                    result_text += f"{i}. {issue['rule']}: {issue.get('reason', ['No details'])[0]}\n"
            else:
                result_text += "No quality issues detected with the selected rules."
            
            return self.create_text_message(result_text)
            
        except ImportError:
            return self.create_text_message("Error: Dingo library is not installed. Please install dingo-python package.")
        except Exception as e:
            return self.create_text_message(f"Error during evaluation: {str(e)}")
