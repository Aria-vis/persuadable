# Decision memo: email everyone, or only the customers the model picks?

## Recommendation

Send the women's-merchandise email to everyone if the gross margin on an extra sale is comfortably above about 35%. If the margin is below about 25%, send it only to the customers the model ranks highest. In between it is close, and targeting is the safer choice because it never lost money across the email costs I tested ($0.10 to $0.50). In every case, use the model to rank customers, not to quote dollar figures.

## The question

A retailer emailed about 21,400 customers a women's merchandise promotion and held back about 21,300 as a control, assigned at random (Hillstrom MineThatData data). Should the next campaign go to everyone, or is it better to pick who gets it?

## What I found

The email works. Site visits rose from 10.6% to 15.1% (+4.5 points, 95% interval 3.9 to 5.2). Purchases rose from 0.57% to 0.88%, and spend per customer rose by about $0.42 (interval $0.18 to $0.70) over the two weeks.

The experiment is trustworthy. The split was 50/50 (p = 0.70), the two groups looked alike on every trait I measured, and the test could have detected an effect as small as 0.85 points on visits.

The effect is not the same for everyone. New customers responded more than existing ones (+5.0 vs +4.0 points), and it varied with how recently someone had bought. Purchase channel made no difference.

I built two uplift models (a T-learner and an S-learner, both XGBoost) and compared them on held-out customers. The S-learner ranked customers better (Qini AUC 0.045 vs 0.018). Emailing the model's top half gave a realized lift of 5.8 points, against 3.6 points for everyone.

The model's predicted sizes are too high. Customers in its "Persuadable" group were predicted at about +12 points and showed about +3 in the test set, and the four bucket labels I tried did not separate customers. I found no evidence that the email puts off any group.

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

