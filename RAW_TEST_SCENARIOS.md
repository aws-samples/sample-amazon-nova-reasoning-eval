# Raw Test Scenarios for Nova Model Evaluation

This file contains the original, unoptimized test scenarios used for evaluating Amazon Nova models. These prompts are intentionally simple and unstructured to establish a baseline.

## Purpose

These raw prompts serve as input to the **Bedrock Prompt Optimizer API**, which analyzes and rewrites them with:
- Clear markdown structure (headers, bullets, sections)
- Better instruction organization
- Improved clarity and scannability
- Model-specific optimizations

## Workflow

1. **Raw prompts** (this file) → 
2. **`option2_prompt_optimizer.py`** (uses Bedrock Prompt Optimizer API) → 
3. **Optimized prompts** (`optimized_prompts_*.json` files) → 
4. **Notebook evaluation** (`nova_lite_reasoning_evals.ipynb`)

## Test Scenarios

### 1. Angry Customer Complaint

**Scenario Name:** Angry Customer Complaint

**Prompt:**
```
You are a customer support representative. A customer writes:

"I am absolutely furious! I ordered a laptop 3 weeks ago and it still hasn't arrived. When I called last week, your representative was rude and unhelpful. I've been a loyal customer for 5 years and this is how you treat me? I want my money back immediately and I'm considering switching to your competitor. This is unacceptable!"

Please provide a professional response that addresses their concerns.
```

**Key Issues:**
- Delayed delivery
- Poor customer service experience
- Customer loyalty concerns
- Refund request

**Required Solutions:**
- Apologize sincerely
- Investigate delivery status
- Offer compensation
- Escalate if needed

**Policies:**
- Always acknowledge customer emotions
- Provide specific next steps
- Offer multiple resolution options

---

### 2. Software Technical Problem

**Scenario Name:** Software Technical Problem

**Prompt:**
```
You are a technical support representative. A customer reports:

"Hi, I'm having trouble with your mobile app. Every time I try to upload a photo, the app crashes. I've tried restarting my phone (iPhone 12, iOS 16.1) and reinstalling the app, but the problem persists. I need to upload these photos for work and this is really frustrating. Can you help me fix this?"

Please provide a helpful technical support response.
```

**Key Issues:**
- App crashing during photo upload
- iPhone 12 with iOS 16.1
- Work-related urgency
- Already tried basic troubleshooting

**Required Solutions:**
- Acknowledge the issue
- Provide advanced troubleshooting steps
- Offer alternative solutions
- Escalate to technical team if needed

**Policies:**
- Provide step-by-step instructions
- Acknowledge customer effort in troubleshooting
- Offer workarounds when possible

---

### 3. Billing Dispute

**Scenario Name:** Billing Dispute

**Prompt:**
```
You are a billing support representative. A customer contacts you:

"I just received my monthly bill and there's a charge for $89.99 that I don't recognize. It says 'Premium Service Upgrade' but I never signed up for any premium service. I've been on the basic plan for 2 years and haven't changed anything. This looks like an error or maybe someone accessed my account without permission. Please remove this charge immediately."

Please provide an appropriate response to resolve this billing issue.
```

**Key Issues:**
- Unrecognized charge
- Premium service upgrade not requested
- Potential unauthorized access concern
- Request for immediate removal

**Required Solutions:**
- Investigate the charge
- Review account activity
- Address security concerns
- Provide resolution timeline

**Policies:**
- Verify customer identity
- Investigate before making changes
- Explain billing processes
- Offer account security review

---

### 4. Product Defect Report

**Scenario Name:** Product Defect Report

**Prompt:**
```
You are a product support representative. A customer reports:

"I bought your wireless headphones 2 months ago and the left earpiece has stopped working completely. There's no sound coming from it at all. The right side works fine. I've tried connecting to different devices and the problem persists. These headphones cost $200 and I expected them to last longer than 2 months. I'd like a replacement or refund. I still have the receipt and original packaging."

Please provide a response that addresses this product defect issue.
```

**Key Issues:**
- Left earpiece not working
- 2-month-old product
- High-value item ($200)
- Customer has receipt and packaging

**Required Solutions:**
- Acknowledge the defect
- Offer replacement or refund
- Explain warranty process
- Provide return instructions

**Policies:**
- Honor warranty terms
- Make return process easy
- Apologize for product quality issues
- Offer expedited replacement when possible

---

### 5. Account Security Concern

**Scenario Name:** Account Security Concern

**Prompt:**
```
You are a security support representative. A customer contacts you urgently:

"Help! I think someone has hacked my account. I just received an email saying my password was changed, but I didn't change it. I also see some purchases in my account history that I didn't make - two items totaling $150. I'm really worried about my personal information and credit card details. What should I do? Can you secure my account immediately?"

Please provide an immediate and comprehensive response to this security incident.
```

**Key Issues:**
- Unauthorized password change
- Fraudulent purchases ($150)
- Personal information at risk
- Credit card security concern

**Required Solutions:**
- Immediately secure the account
- Investigate fraudulent activity
- Reverse unauthorized charges
- Provide security recommendations

**Policies:**
- Act quickly on security issues
- Verify customer identity thoroughly
- Document all security incidents
- Provide clear next steps

---

## Usage Notes

### For Prompt Optimization:

Run the optimizer script to generate optimized versions:

```bash
python option2_prompt_optimizer.py
```

This will:
1. Use the official AWS Bedrock Prompt Optimizer API
2. Generate model-specific optimized prompts
3. Save them to `optimized_prompts_*.json` files
4. Create one file per Nova model (Lite, Micro, Pro, Premier)

### For Evaluation:

The notebook `nova_lite_reasoning_evals.ipynb` automatically loads optimized prompts from the JSON files. If the JSON files don't exist, you'll see an error message prompting you to run the optimizer first.

### Comparison:

To compare raw vs optimized prompts:
1. Look at the prompts in this file (raw)
2. Look at the prompts in the JSON files (optimized)
3. Notice the improved structure, clarity, and organization

## Expected Improvements

After optimization, prompts typically show:
- **2-3x length increase** (more detailed instructions)
- **Clear markdown structure** (headers, bullets, sections)
- **Explicit instructions** (numbered steps, clear expectations)
- **Better context** (role clarification, scenario framing)
- **Improved scannability** (easier for models to parse)

## Model-Specific Optimizations

The Bedrock Prompt Optimizer tailors prompts for each model:
- **Nova Lite**: Concise, clear, efficient structure
- **Nova Micro**: Ultra-simple, direct instructions
- **Nova Pro**: Complex, detailed, multi-section prompts
- **Nova Premier**: Sophisticated, well-organized hierarchies

Each model gets prompts optimized for its specific capabilities and characteristics.
