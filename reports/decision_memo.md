# Decision memo: email everyone, or only the customers the model picks?

## Recommendation

Send the women's-merchandise email to everyone if the gross margin on an extra sale is comfortably above about 35%. If the margin is below about 25%, send it only to the customers the model ranks highest. In between it is close, and targeting is the safer choice because it never lost money across the email costs I tested ($0.10 to $0.50). In every case, use the model to rank customers, not to quote dollar figures.

## The question

A retailer emailed about 21,400 customers a women's merchandise promotion and held back about 21,300 as a control, assigned at random (Hillstrom MineThatData data). Should the next campaign go to everyone, or is it better to pick who gets it?

## What I found

The campaign drove clear, statistically significant gains across the entire funnel during the two-week tracking window. Overall site visits increased from 10.6% in control to 15.1% in treatment (+4.5 percentage points, 95% CI 3.9 to 5.2 pp). Conversion rose from 0.57% to 0.88%, and mean customer spend increased by $0.42 (bootstrap 95% CI $0.18 to $0.70).

The underlying A/B test data is clean and reliable. The randomization produced an even 50/50 assignment (SRM p = 0.70), balance tests across all seven baseline customer covariates showed no pre-treatment differences after FDR adjustment, and the trial was well-powered (retrospective visit MDE of 0.85 pp).

Treatment response was heterogeneous. First-time buyers reacted more strongly than established customers (+5.0 pp vs. +4.0 pp lift), and responsiveness varied significantly by purchase recency, whereas purchase channel (Web vs. Phone vs. Multichannel) had no moderating effect.

To capture this heterogeneity, I trained XGBoost-based T-Learner and S-Learner models on 70% of the data and evaluated them on the remaining 30% holdout. The S-Learner ordered customers substantially better, achieving a Qini AUC of 0.045 versus 0.018 for the T-Learner. In practice, targeting the S-Learner's top 50% produced a realized lift of 5.8 pp, compared to 3.6 pp across the full test cohort.

However, the model's raw uplift magnitudes were inflated by estimation noise in the tails. Customers sorted into the theoretical "Persuadable" tier were predicted to gain +11.8 pp but realized only +3.1 pp in the randomized test set. Furthermore, customers assigned to the "Sleeping Dog" tier still achieved a +3.1 pp lift (95% CI -0.4 to +6.5 pp), indicating no real customer backlash. While the four conceptual buckets failed to separate customers in practice, the model's continuous percentile ranking proved dependable for targeting.

## What it means in money

I valued an extra visit at $7.90 (average spend per visitor in the training data) and assumed an email costs $0.10. On held-out customers:

| Policy | Net value per 1,000 customers |
|---|---|
| Email everyone | $184 |
| Email the model's picks (70% of customers) | $163 |

The $21 gap is within noise (interval -$69 to +$25), so at $0.10 the model adds nothing over emailing everyone.

Emailing everyone stops paying at about $0.28 per email. From $0.30 the model's list clearly wins (+$95 per 1,000 customers, interval +$36 to +$151), mostly by avoiding losses: at $0.50 it only breaks even.

These are revenue figures. A lower margin acts like a higher email cost: divide the cost by the margin. A 33% margin makes a $0.10 email behave like a $0.30 one, and a 20% margin like $0.50. On the held-out data, emailing everyone needs a margin of about 35% to pay; on the full experiment's spend figures the number is about 24%. That spread is why the recommendation has a middle zone.

## Decision

Ship the campaign. Email everyone if the margin is above about 35%; target if it is below about 25%. Before relying on the model's targeting, run a small fresh test on the targeted list, because everything here comes from one historical experiment.

## Limits

- Two weeks of outcomes, one retailer, historical data I did not design.
- I chose the winning model and scored the policies on the same test set, so the comparison is slightly optimistic for the model.
- One 70/30 split. That test set showed a lower lift (3.6 points) than the full experiment (4.5), so on the full data the crossover cost would be higher, around $0.36.
- An extra visit is valued at the average visitor's spend, and the figures are revenue, not profit.
- I did not test a top-k% cutoff, which might beat the predicted-uplift threshold I used.
