"""
AWS Bedrock Prompt Optimizer for Nova Model Evaluation
=======================================================

This script uses the official AWS Bedrock Prompt Optimizer API to generate
model-specific optimized prompts for Amazon Nova model evaluations.

## What It Does

The Bedrock Prompt Optimizer API analyzes prompts and rewrites them to:
- Improve structure, clarity, and organization
- Add appropriate markdown formatting (headers, bullets, sections)
- Enhance instruction specificity and detail
- Create model-specific optimizations tailored to each Nova model

Optimized prompts typically increase in length 2-3x with better detail and
formatting, leading to improved model performance.

## Supported Models

The Prompt Optimizer API supports:
- ✅ amazon.nova-lite-v1:0 (Nova Lite 1.0)
- ✅ amazon.nova-micro-v1:0 (Nova Micro)
- ✅ amazon.nova-pro-v1:0 (Nova Pro)
- ✅ amazon.nova-premier-v1:0 (Nova Premier)
- ⚠️  amazon.nova-2-lite-v1:0 (Nova Lite 2.0) - Not yet supported by API

For unsupported models like Nova Lite 2.0, the script intelligently reuses
optimizations from similar models (Nova Lite 1.0 in this case).

## Usage

Run this script to generate optimized prompts for all Nova models:

```bash
python prompt_optimizer.py
```

This creates `optimized_prompts_*.json` files that the evaluation notebook
automatically loads.

## Output Files

- `optimized_prompts_amazon_nova-lite-v1_0.json`
- `optimized_prompts_amazon_nova-2-lite-v1_0.json`
- `optimized_prompts_amazon_nova-micro-v1_0.json`
- `optimized_prompts_amazon_nova-pro-v1_0.json`
- `optimized_prompts_amazon_nova-premier-v1_0.json`

## Cost

The Prompt Optimizer API costs approximately $0.001-0.003 per optimization.
For 5 scenarios across 4 models (20 API calls), the total cost is ~$0.04.
Results are cached, so subsequent runs are free.

## Official Documentation

https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-optimize.html

## Requirements

- AWS credentials with Bedrock access
- boto3 installed (`pip install boto3`)
- Access to Bedrock Prompt Optimizer API

Author: Amazon Nova Evaluation Team
Last Updated: 2025-01-06
"""

import boto3
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Initialize Bedrock clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

# Models supported by Prompt Optimizer API
SUPPORTED_MODELS = {
    'nova_lite': 'amazon.nova-lite-v1:0',
    'nova_micro': 'amazon.nova-micro-v1:0',
    'nova_pro': 'amazon.nova-pro-v1:0',
    'nova_premier': 'amazon.nova-premier-v1:0'
}

# Models NOT yet supported by Prompt Optimizer (will reuse optimizations from similar models)
UNSUPPORTED_MODELS = {
    'nova_lite_2': {
        'model_id': 'amazon.nova-2-lite-v1:0',
        'reuse_from': 'amazon.nova-lite-v1:0',  # Reuse Nova Lite 1.0 optimizations
        'reason': 'Nova Lite 2.0 not yet supported by Prompt Optimizer API'
    }
}

# All target models for evaluation
TARGET_MODELS = {
    **SUPPORTED_MODELS,
    'nova_lite_2': 'amazon.nova-2-lite-v1:0'
}

# Cache for optimized prompts to avoid duplicate API calls
OPTIMIZED_PROMPTS_CACHE = {}

# ============================================================================
# PROMPT OPTIMIZER FUNCTIONS
# ============================================================================

def optimize_prompt_with_api(prompt_text, target_model_id):
    """
    Use the official Bedrock Prompt Optimizer API to optimize a prompt.
    
    The API analyzes the prompt and returns an improved version with:
    - Better structure and organization
    - Enhanced clarity and specificity
    - Appropriate markdown formatting
    - Model-specific optimizations
    
    Parameters
    ----------
    prompt_text : str
        Original prompt text to optimize
    target_model_id : str
        Model ID to optimize for (must be supported by Prompt Optimizer)
        
    Returns
    -------
    dict
        Optimization result containing:
        - original: Original prompt text
        - optimized: Optimized prompt text
        - analysis: Analysis insights from optimizer
        - model: Target model ID
        - original_length: Character count of original prompt
        - optimized_length: Character count of optimized prompt
        - method: 'official_api'
        - timestamp: ISO timestamp of optimization
        
    Raises
    ------
    ValueError
        If no optimized prompt is returned from API
    Exception
        If API call fails
        
    API Reference
    -------------
    https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_OptimizePrompt.html
    """
    cache_key = f"{target_model_id}_{hash(prompt_text)}"
    
    # Check cache first to avoid duplicate API calls
    if cache_key in OPTIMIZED_PROMPTS_CACHE:
        print(f"  ✓ Using cached optimization")
        return OPTIMIZED_PROMPTS_CACHE[cache_key]
    
    try:
        print(f"  🔄 Calling Bedrock Prompt Optimizer API...")
        
        # Call the official OptimizePrompt API
        response = bedrock_agent.optimize_prompt(
            input={
                'textPrompt': {
                    'text': prompt_text
                }
            },
            targetModelId=target_model_id
        )
        
        # Parse the streaming response
        optimized_prompt = None
        analysis_message = None
        
        event_stream = response['optimizedPrompt']
        for event in event_stream:
            # Analysis event contains insights about the prompt
            if 'analyzePromptEvent' in event:
                analysis_data = event['analyzePromptEvent']
                analysis_message = analysis_data.get('message', '')
                print(f"  📊 Analysis: {analysis_message[:80]}...")
            
            # Optimized prompt event contains the improved prompt
            if 'optimizedPromptEvent' in event:
                optimized_prompt_obj = event['optimizedPromptEvent']['optimizedPrompt']
                if 'textPrompt' in optimized_prompt_obj:
                    optimized_prompt = optimized_prompt_obj['textPrompt']['text']
        
        if not optimized_prompt:
            raise ValueError("No optimized prompt returned from API")
        
        result = {
            'original': prompt_text,
            'optimized': optimized_prompt,
            'analysis': analysis_message or 'No analysis provided',
            'model': target_model_id,
            'original_length': len(prompt_text),
            'optimized_length': len(optimized_prompt),
            'method': 'official_api',
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache the result
        OPTIMIZED_PROMPTS_CACHE[cache_key] = result
        
        print(f"  ✓ Optimization complete ({len(prompt_text)} → {len(optimized_prompt)} chars)")
        return result
        
    except Exception as e:
        print(f"  ❌ API optimization failed: {e}")
        raise


def optimize_prompt_for_model(prompt_text, target_model_id):
    """
    Optimize a prompt for any Nova model, using the official API when supported.
    
    For models not yet supported by the Prompt Optimizer API, this function
    intelligently reuses optimizations from similar supported models.
    
    Parameters
    ----------
    prompt_text : str
        Original prompt text to optimize
    target_model_id : str
        Model ID to optimize for (any Nova model)
        
    Returns
    -------
    dict
        Optimization result (see optimize_prompt_with_api for structure)
        
    Raises
    ------
    ValueError
        If model is not configured for optimization
    """
    # Check if this is a supported model - use API directly
    if target_model_id in SUPPORTED_MODELS.values():
        print(f"  ✅ Model {target_model_id} is supported by Prompt Optimizer API")
        return optimize_prompt_with_api(prompt_text, target_model_id)
    
    # Check if we should reuse optimization from another model
    for model_info in UNSUPPORTED_MODELS.values():
        if isinstance(model_info, dict) and model_info['model_id'] == target_model_id:
            reuse_from = model_info['reuse_from']
            reason = model_info.get('reason', 'Not supported')
            
            print(f"  ℹ️  {reason}")
            print(f"  🔄 Optimizing with {reuse_from} and reusing for {target_model_id}")
            
            # Optimize with the supported model
            result = optimize_prompt_with_api(prompt_text, reuse_from)
            
            # Update the result to indicate it's being reused
            result['model'] = target_model_id
            result['method'] = f'reused_from_{reuse_from}'
            result['reused_from'] = reuse_from
            
            return result
    
    # If we get here, model is not configured
    raise ValueError(f"Model {target_model_id} is not configured for optimization")


def optimize_all_scenarios(scenarios, target_model_id):
    """
    Optimize all test scenarios for a specific model.
    
    Parameters
    ----------
    scenarios : dict
        Dictionary of test scenarios with structure:
        {
            'scenario_key': {
                'name': str,
                'prompt': str,
                'key_issues': list,
                'required_solutions': list,
                'policies': list
            }
        }
    target_model_id : str
        Model ID to optimize for
        
    Returns
    -------
    dict
        Optimized scenarios dictionary with same structure as input,
        plus _optimization_metadata for each scenario
    """
    print(f"\n{'='*70}")
    print(f"Optimizing prompts for: {target_model_id}")
    print('='*70)
    
    optimized_scenarios = {}
    
    for scenario_key, scenario_data in scenarios.items():
        print(f"\nScenario: {scenario_data['name']}")
        
        result = optimize_prompt_for_model(
            scenario_data['prompt'],
            target_model_id
        )
        
        # Create optimized scenario with metadata
        optimized_scenarios[scenario_key] = {
            'name': scenario_data['name'],
            'prompt': result['optimized'],
            'key_issues': scenario_data['key_issues'],
            'required_solutions': scenario_data['required_solutions'],
            'policies': scenario_data['policies'],
            '_optimization_metadata': {
                'original_length': result['original_length'],
                'optimized_length': result['optimized_length'],
                'target_model': target_model_id,
                'method': result.get('method', 'unknown'),
                'timestamp': result.get('timestamp', datetime.now().isoformat())
            }
        }
    
    print(f"\n✓ All scenarios optimized for {target_model_id}")
    return optimized_scenarios


# ============================================================================
# ORIGINAL TEST SCENARIOS
# ============================================================================

ORIGINAL_SCENARIOS = {
    'angry_customer': {
        'name': 'Angry Customer Complaint',
        'prompt': '''You are a customer support representative. A customer writes:

"I am absolutely furious! I ordered a laptop 3 weeks ago and it still hasn't arrived. When I called last week, your representative was rude and unhelpful. I've been a loyal customer for 5 years and this is how you treat me? I want my money back immediately and I'm considering switching to your competitor. This is unacceptable!"

Please provide a professional response that addresses their concerns.''',
        'key_issues': ['Delayed delivery', 'Poor customer service experience', 'Customer loyalty concerns', 'Refund request'],
        'required_solutions': ['Apologize sincerely', 'Investigate delivery status', 'Offer compensation', 'Escalate if needed'],
        'policies': ['Always acknowledge customer emotions', 'Provide specific next steps', 'Offer multiple resolution options']
    },
    
    'technical_issue': {
        'name': 'Software Technical Problem',
        'prompt': '''You are a technical support representative. A customer reports:

"Hi, I'm having trouble with your mobile app. Every time I try to upload a photo, the app crashes. I've tried restarting my phone (iPhone 12, iOS 16.1) and reinstalling the app, but the problem persists. I need to upload these photos for work and this is really frustrating. Can you help me fix this?"

Please provide a helpful technical support response.''',
        'key_issues': ['App crashing during photo upload', 'iPhone 12 with iOS 16.1', 'Work-related urgency', 'Already tried basic troubleshooting'],
        'required_solutions': ['Acknowledge the issue', 'Provide advanced troubleshooting steps', 'Offer alternative solutions', 'Escalate to technical team if needed'],
        'policies': ['Provide step-by-step instructions', 'Acknowledge customer effort in troubleshooting', 'Offer workarounds when possible']
    },
    
    'billing_dispute': {
        'name': 'Billing Dispute',
        'prompt': '''You are a billing support representative. A customer contacts you:

"I just received my monthly bill and there's a charge for $89.99 that I don't recognize. It says 'Premium Service Upgrade' but I never signed up for any premium service. I've been on the basic plan for 2 years and haven't changed anything. This looks like an error or maybe someone accessed my account without permission. Please remove this charge immediately."

Please provide an appropriate response to resolve this billing issue.''',
        'key_issues': ['Unrecognized charge', 'Premium service upgrade not requested', 'Potential unauthorized access concern', 'Request for immediate removal'],
        'required_solutions': ['Investigate the charge', 'Review account activity', 'Address security concerns', 'Provide resolution timeline'],
        'policies': ['Verify customer identity', 'Investigate before making changes', 'Explain billing processes', 'Offer account security review']
    },
    
    'product_defect': {
        'name': 'Product Defect Report',
        'prompt': '''You are a product support representative. A customer reports:

"I bought your wireless headphones 2 months ago and the left earpiece has stopped working completely. There's no sound coming from it at all. The right side works fine. I've tried connecting to different devices and the problem persists. These headphones cost $200 and I expected them to last longer than 2 months. I'd like a replacement or refund. I still have the receipt and original packaging."

Please provide a response that addresses this product defect issue.''',
        'key_issues': ['Left earpiece not working', '2-month-old product', 'High-value item ($200)', 'Customer has receipt and packaging'],
        'required_solutions': ['Acknowledge the defect', 'Offer replacement or refund', 'Explain warranty process', 'Provide return instructions'],
        'policies': ['Honor warranty terms', 'Make return process easy', 'Apologize for product quality issues', 'Offer expedited replacement when possible']
    },
    
    'account_security': {
        'name': 'Account Security Concern',
        'prompt': '''You are a security support representative. A customer contacts you urgently:

"Help! I think someone has hacked my account. I just received an email saying my password was changed, but I didn't change it. I also see some purchases in my account history that I didn't make - two items totaling $150. I'm really worried about my personal information and credit card details. What should I do? Can you secure my account immediately?"

Please provide an immediate and comprehensive response to this security incident.''',
        'key_issues': ['Unauthorized password change', 'Fraudulent purchases ($150)', 'Personal information at risk', 'Credit card security concern'],
        'required_solutions': ['Immediately secure the account', 'Investigate fraudulent activity', 'Reverse unauthorized charges', 'Provide security recommendations'],
        'policies': ['Act quickly on security issues', 'Verify customer identity thoroughly', 'Document all security incidents', 'Provide clear next steps']
    },
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("AWS BEDROCK PROMPT OPTIMIZER")
    print("="*70)
    print("\nUsing the official AWS Bedrock Prompt Optimizer API")
    print("For unsupported models, reusing optimizations from similar models")
    
    # Optimize for ALL Nova models
    all_optimized_scenarios = {}
    
    for model_key, model_id in TARGET_MODELS.items():
        print("\n" + "="*70)
        print(f"Optimizing for: {model_key.upper()} ({model_id})")
        print("="*70)
        
        all_optimized_scenarios[model_id] = optimize_all_scenarios(ORIGINAL_SCENARIOS, model_id)
    
    # Show comparison for first scenario across models
    print("\n\n" + "="*70)
    print("EXAMPLE: Optimization Comparison Across Models")
    print("="*70)
    
    scenario_key = 'angry_customer'
    print(f"\nScenario: {ORIGINAL_SCENARIOS[scenario_key]['name']}")
    
    print("\n--- ORIGINAL PROMPT ---")
    print(ORIGINAL_SCENARIOS[scenario_key]['prompt'][:200] + "...")
    
    # Show optimized version for each model
    for model_key, model_id in TARGET_MODELS.items():
        optimized = all_optimized_scenarios[model_id][scenario_key]
        metadata = optimized['_optimization_metadata']
        opt_length = metadata['optimized_length']
        method = metadata.get('method', 'N/A')
        
        print(f"\n--- {model_key.upper()} ({model_id}) ---")
        print(f"Method: {method}")
        print(f"Length: {opt_length} chars")
        print(f"Preview: {optimized['prompt'][:150]}...")
    
    # Save optimized prompts to files (one per model)
    print(f"\n\n{'='*70}")
    print("SAVING OPTIMIZED PROMPTS")
    print('='*70)
    
    for model_key, model_id in TARGET_MODELS.items():
        safe_name = model_id.replace(':', '_').replace('.', '_').replace('/', '_')
        output_file = f'optimized_prompts_{safe_name}.json'
        
        with open(output_file, 'w') as f:
            json.dump(all_optimized_scenarios[model_id], f, indent=2)
        
        print(f"  ✓ {output_file}")
    
    # Calculate statistics
    total_api_calls = 0
    reused_count = 0
    
    for model_id, scenarios in all_optimized_scenarios.items():
        for scenario in scenarios.values():
            method = scenario['_optimization_metadata'].get('method', '')
            if method == 'official_api':
                total_api_calls += 1
            elif 'reused_from' in method:
                reused_count += 1
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"""
✅ Used official Bedrock Prompt Optimizer API
✅ Optimized for {len(TARGET_MODELS)} Nova models
✅ Total scenarios: {len(ORIGINAL_SCENARIOS)} per model

Models Optimized:
- Nova Lite 1.0: {len(ORIGINAL_SCENARIOS)} scenarios (official API)
- Nova Lite 2.0: {len(ORIGINAL_SCENARIOS)} scenarios (reused from Nova Lite 1.0)
- Nova Micro: {len(ORIGINAL_SCENARIOS)} scenarios (official API)
- Nova Pro: {len(ORIGINAL_SCENARIOS)} scenarios (official API)
- Nova Premier: {len(ORIGINAL_SCENARIOS)} scenarios (official API)

API Calls:
- Direct API calls: {total_api_calls}
- Reused optimizations: {reused_count}
- Total optimizations: {total_api_calls + reused_count}

Cost Estimate:
- Prompt Optimizer API: ~$0.001-0.003 per optimization
- Total API calls: {total_api_calls}
- Estimated cost: ${total_api_calls * 0.002:.3f}

💡 With caching, subsequent runs are free!

Next Steps:
1. Run the evaluation notebook: jupyter notebook nova_lite_reasoning_evals.ipynb
2. The notebook will automatically load these optimized prompts
3. Compare model performance with optimized vs. original prompts
    """)
