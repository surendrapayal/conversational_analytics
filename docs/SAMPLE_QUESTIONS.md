Here are **2-3 analytical questions for each table** in the schema:

## **1. Customers**
1. Which customers have never placed an order, and what is their account creation pattern?
2. What percentage of customers have loyalty accounts, and how does customer lifetime value differ between loyalty members and non-members?
3. How many unique customers have made repeat purchases, and what is the average frequency of repeat orders?

## **2. Discounts**
1. Which discounts have the highest redemption rate and generate the most revenue impact?
2. What is the utilization trend for discounts by start/end date, and are seasonal discounts more effective than year-round ones?
3. Which discount type (percentage vs. fixed amount) drives higher average order values?

## **3. Employee**
1. Which employees have the longest tenure, and how do their sales/order volumes compare to newer hires?
2. How many employees per role and location are currently active, and what is staff turnover by location?
3. Do employees hired at certain times show different performance metrics compared to other hire cohorts?

## **4. Ingredients**
1. Which ingredients are used most frequently across all recipes, and what is their average stock level?
2. What is the ingredient diversity per menu item, and are there common ingredients that could reduce supplier complexity?
3. Which ingredients have the highest variance in unit costs across suppliers?

## **5. Inventory**
1. Which ingredient-location combinations are below reorder threshold, and what is the risk of stockouts?
2. What is the inventory turnover rate by ingredient and location, and are there items with excessive stock?
3. Which locations have the highest inventory value, and how does storage efficiency vary by location?

## **6. Location**
1. Which location generates the highest revenue per square table capacity?
2. How do order volumes, average order values, and customer satisfaction vary by location and timezone?
3. Which location has the most efficient employee-to-order ratio?

## **7. Loyalty_Accounts**
1. What is the distribution of loyalty points balance across customers, and how many are close to redemption thresholds?
2. What percentage of loyalty account holders are active (made purchases in last 30/90 days)?
3. How does loyalty program participation correlate with customer retention and lifetime value?

## **8. Loyalty_Txn**
1. What is the earn-to-redeem ratio, and how long does it take customers to accumulate redeemable points?
2. Which transaction types (earn vs. redeem) dominate by time period, and are there seasonal patterns?
3. What is the average points balance change per customer per month, and are there high-velocity earners vs. slow-burn customers?

## **9. Menu_Categories**
1. Which menu category generates the highest revenue and has the highest order frequency?
2. What is the profit margin and average unit price by category?
3. How does category performance vary by location and time of day/week?

## **10. Menu_Items**
1. Which active menu items have the lowest order frequency and are candidates for removal?
2. What is the correlation between menu item price and order volume across categories?
3. Which menu items are sold together most frequently, and could they be bundled?

## **11. Order_Discounts**
1. What percentage of orders use discounts, and which discounts are most frequently applied together?
2. How much revenue is lost to discounts by type and time period?
3. Do customers who use discounts have higher repeat purchase rates?

## **12. Order_Items**
1. Which menu items have the highest variance in unit price (indicating frequent price changes)?
2. What is the average number of items per order, and how does it affect order completion rates?
3. Which menu items have the lowest/highest margins when accounting for actual unit price paid?

## **13. Orders**
1. What is the average order value, completion rate, and cancellation rate by location, time of day, and customer type (loyalty vs. walk-in)?
2. How long is the average time-to-payment from order placement, and which order statuses are stuck in "open"?
3. Which employees process the most orders, and what is their average order value vs. other staff?

## **14. Payments**
1. What is the payment success rate by payment method, and what is the failure/refund rate trend?
2. How much revenue is collected via each payment method, and what is the average payment amount?
3. Is there a correlation between payment method and order cancellation or refund likelihood?

## **15. Recipe_Items**
1. Which ingredients are critical (used in many recipes), and what is the risk if they become unavailable?
2. What is the average number of ingredients per menu item, and are complex recipes more profitable?
3. Which recipes require rare or expensive ingredients that could impact margin?

## **16. Reservations**
1. What is the no-show rate for reservations, and how does it correlate with booking lead time?
2. Which tables have the highest reservation-to-order conversion rate?
3. How many reservations result in actual orders, and what is the average order value from reserved vs. walk-in tables?

## **17. Roles**
1. How many employees are in each role, and what is the role distribution by location?
2. What is the average order volume and revenue generated per employee by role?
3. Which roles have the highest turnover, and what is the cost per hire by role?

## **18. Shifts**
1. What is the total labor hours by location and shift time, and how does it correlate with order volume?
2. Which shift times are understaffed or overstaffed based on order demand?
3. Are there employees scheduled during overlapping shifts, and what is the labor cost efficiency?

## **19. Supplier**
1. How many ingredients does each supplier provide, and what is the supplier concentration risk?
2. Which suppliers have the best pricing for critical ingredients?
3. How does supplier reliability (delivery timeliness) correlate with inventory levels?

## **20. Supplier_Items**
1. Which ingredients have the highest price variance across suppliers, indicating negotiation opportunities?
2. What is the total cost of goods by supplier, and which suppliers contribute the most to COGS?
3. For each ingredient, what is the cost difference between the cheapest and most expensive supplier?

## **21. Tables**
1. What is the utilization rate and average turnaround time per table by location?
2. How does table capacity utilization affect revenue per table, and are there optimal table sizes?
3. Which tables have the highest order value and longest average customer dwell time?

---

These questions span **operational efficiency, revenue optimization, risk management, and strategic planning** across your restaurant business model.

## **Customer & Orders Analytics**
1. Which customers have the highest total spending across all their orders, and what is their loyalty points balance?
2. What is the average order value per customer, and how do customers using discounts compare to those without discounts?
3. How many orders per location were placed by registered customers vs. walk-ins, and what is the average order amount for each?

## **Menu & Order Items Analytics**
1. Which menu items are most frequently ordered together, and what is their combined average revenue per order?
2. How do menu items perform by category in terms of order frequency, total revenue, and current inventory availability?
3. Which inactive menu items had the highest sales before being deactivated, and what ingredients do they require?

## **Payments & Discounts Analytics**
1. What is the payment success rate by payment method, and how much revenue is impacted by failed or refunded payments?
2. How effective are discounts in driving order volume—do orders with discounts have higher average values or frequency than those without?
3. What is the discount utilization rate by discount code, and which discounts generate the most revenue impact?

## **Employees & Shifts Analytics**
1. Which employees (by role and location) process the most orders, and how does their shift schedule correlate with order volume?
2. How many hours per week does each employee work across their shifts, and which locations have the most scheduling variance?

## **Inventory & Recipes Analytics**
1. Which ingredients are running low across locations relative to their reorder thresholds, and which menu items depend on these ingredients?
2. What is the ingredient cost per menu item based on current supplier pricing, and how does it relate to menu item pricing?

## **Reservations & Tables Analytics**
1. What is the table utilization rate by location—how many reservations actually result in orders, and what is the no-show rate?
2. Which tables have the highest occupancy rate and average order value, and should capacity be adjusted?

## **Loyalty Program Analytics**
1. What is the customer retention rate for loyalty program members, and how does their spending compare to non-members?
2. Which customers are closest to redeeming rewards, and what incentive campaigns could drive engagement?

---

Here are **analytical questions that require joining multiple tables**:

## **3-Table Joins**

1. **Customers → Orders → Payments**
   - What is the total revenue and average order value per customer, including payment method distribution?
   - Which customers have the highest failed payment rates, and how many retries before successful payment?

2. **Customers → Loyalty_Accounts → Loyalty_Txn**
   - Which customers have earned but never redeemed loyalty points, and how long have they held points?
   - What is the earn-to-redemption ratio by customer, and which customers are closest to redemption thresholds?

3. **Orders → Employee → Roles**
   - Which employee roles generate the highest average order values and process the most orders?
   - How do order completion rates and tip amounts vary by employee role?

4. **Orders → Tables → Location**
   - What is the table utilization rate and revenue per table by location?
   - Which locations have the highest revenue-per-table-capacity ratio?

5. **Employees → Shifts → Location**
   - How many labor hours per location per day/week/month are scheduled, and how does it correlate with order volume?
   - Which locations are over/understaffed during specific shift times?

6. **Ingredients → Inventory → Location**
   - Which ingredient-location combinations are below reorder threshold and need urgent restocking?
   - What is the total inventory value by location and ingredient?

7. **Reservations → Tables → Location**
   - What is the reservation-to-dine conversion rate by location and table type?
   - How many reservation no-shows occur per location, and what is the revenue impact?

---

## **4-Table Joins**

8. **Customers → Orders → Order_Items → Menu_Items**
   - Which customers purchase the same menu items repeatedly, and what is their loyalty status?
   - What is the customer lifetime value broken down by menu item category?

9. **Orders → Order_Items → Menu_Items → Menu_Categories**
   - Which menu categories generate the most revenue per location, and how do they perform by time of day?
   - What is the average order size (items per order) by menu category?

10. **Orders → Order_Discounts → Discounts + Customers**
    - Which discount codes drive the highest order frequency and customer retention?
    - What is the incremental revenue impact of discounts vs. orders without discounts?

11. **Menu_Items → Recipe_Items → Ingredients → Supplier_Items**
    - What is the ingredient cost per menu item based on current supplier pricing?
    - Which menu items have the highest ingredient cost relative to selling price?

12. **Ingredients → Supplier_Items → Supplier + Inventory**
    - Which suppliers offer the best pricing for critical ingredients by location?
    - What is the cost variance for the same ingredient across multiple suppliers?

13. **Employee → Orders → Order_Items → Menu_Items**
    - Which employees sell specific menu items most frequently, and what is their average order value?
    - How do employee performance metrics vary by menu category?

14. **Orders → Employee → Shifts + Location**
    - Which employees work during peak order times, and what is their productivity (orders/hour)?
    - How does labor cost per order vary by employee and shift time?

15. **Customers → Orders → Payments + Order_Discounts**
    - What is the effective discount rate applied to orders, and how does it impact payment success rates?
    - Do customers using discounts have higher or lower payment failure rates?

---

## **5-Table Joins**

16. **Customers → Orders → Order_Items → Menu_Items → Menu_Categories**
    - What menu categories does each customer prefer, and how does this correlate with spending?
    - Which customer segments (by spending) favor which categories?

17. **Orders → Order_Items → Menu_Items → Recipe_Items → Ingredients**
    - For each order, what is the total ingredient cost, and how does it compare to the selling price (profit margin)?
    - Which orders use the most expensive ingredients, and are they priced accordingly?

18. **Menu_Items → Recipe_Items → Ingredients → Inventory → Location**
    - How many menu items can be prepared at each location based on current ingredient inventory?
    - Which menu items pose the highest stockout risk by location?

19. **Menu_Items → Recipe_Items → Ingredients → Supplier_Items → Supplier**
    - For each menu item, what is the minimum cost if we source from the cheapest supplier for each ingredient?
    - What is the cost difference between current supplier selection and optimal supplier selection?

20. **Orders → Employee → Shifts → Location + Customers**
    - Which employees at which locations serve which customer segments (loyalty vs. walk-in)?
    - What is the revenue generated per employee per shift per location?

21. **Customers → Loyalty_Accounts → Loyalty_Txn → Orders → Payments**
    - How do loyalty program members' spending and payment patterns differ from non-members?
    - What is the ROI of the loyalty program (total points issued vs. redemptions vs. incremental revenue)?

---

## **6-Table Joins**

22. **Orders → Order_Items → Menu_Items → Recipe_Items → Ingredients → Inventory**
    - When an order is placed, are all required ingredients in stock at that location?
    - What is the fulfillment rate by location (% of orders that could be fulfilled with current inventory)?

23. **Orders → Order_Items → Menu_Items → Recipe_Items → Ingredients → Supplier_Items**
    - For completed orders, what was the actual ingredient cost based on recipe quantities?
    - How does margin vary per order based on ingredient costs and menu prices?

24. **Customers → Orders → Employee → Shifts → Location + Roles**
    - Which customer types (by spending/loyalty) are served by which roles at which locations during which shifts?
    - What is the customer satisfaction/repeat rate by employee role, location, and shift?

25. **Orders → Reservations → Tables → Location + Customers + Employee**
    - What percentage of reservations result in actual orders, and what is the average order value?
    - How do reservation-based orders differ from walk-in orders in terms of value, items, and completion?

26. **Menu_Items → Recipe_Items → Ingredients → Inventory → Supplier_Items → Supplier**
    - For each menu item, what is the production cost at each location (based on local inventory + supplier pricing)?
    - Which menu items have location-dependent profitability?

---

## **7+ Table Joins**

27. **Customers → Orders → Order_Items → Menu_Items → Recipe_Items → Ingredients → Inventory**
    - For each customer order placed, what was the inventory position before and after for each ingredient at that location?
    - Which orders caused inventory to fall below reorder threshold?

28. **Orders → Employee → Roles + Shifts + Location → Customers → Order_Items → Menu_Items**
    - By employee role, location, shift time: what is the order count, revenue, average order value, and items per order?
    - Which combinations are most profitable and should be optimized?

29. **Customers → Orders → Order_Discounts → Discounts + Payments + Loyalty_Accounts → Loyalty_Txn**
    - For loyalty members using discounts: what is the actual discount impact on loyalty point accumulation?
    - Do loyalty members redeem points faster when discounts are applied?

30. **Menu_Items → Recipe_Items → Ingredients → Supplier_Items → Supplier + Inventory + Orders → Order_Items**
    - For each menu item ordered: what was the ingredient cost from supplier, current inventory, and sale price?
    - Calculate realized margin per order based on actual ingredient sourcing and pricing.

---

These questions span **revenue optimization, operational efficiency, cost analysis, customer segmentation, and inventory management** and all require strategic joining of multiple tables.