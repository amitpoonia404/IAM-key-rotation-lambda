# IAM-key-rotation-lambda
Lambda function to rotate IAM user keys
1. Create Lambda with necessary IAM role attached to it
2. Create a CloudWatch event rule to schedule automatic rotation. 
Goto CloudWatch->Events->Rule->Create Rule 
Create a rule with schedule at a fixed rate of desired days (like 90 days) and inside Targets choose above Lambda function, put below value in Configure input --> Constant(JSON Text)
**{"action":"create","username":"nameofIAMuser"}**
Enable this rule.

3. To test the Lambda, create a test event with {"action":"create","username":"nameofIAMuser"} and run.
