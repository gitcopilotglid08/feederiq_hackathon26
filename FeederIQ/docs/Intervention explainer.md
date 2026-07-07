**Purpose**
The planning prototype evaluates a set of candidate interventions that can reduce feeder stress caused by future EV demand, solar adoption, and data center load growth. These interventions are modeled as simplified but interpretable planning levers. 
Each intervention can be applied at one of three levels:
•	33 = low / partial implementation
•	66 = medium / moderate implementation
•	100 = high / aggressive implementation
A level of 0 means the intervention is not used.
________________________________________
1. Battery
What the battery intervention represents
The battery intervention represents a distributed or feeder-level battery energy storage system used for peak shaving. Its goal is to reduce feeder demand during evening peak hours and slightly increase demand during midday charging hours.
This is a common non-wires alternative in grid planning because batteries can:
•	reduce peak load seen by transformers and lines
•	support voltage during peak demand
•	defer conventional network upgrades
•	absorb energy during lower-stress hours and discharge during high-stress hours
________________________________________
How is it implemented:
•	during 17:00–21:00, the battery discharges and reduces feeder demand
•	during 11:00–14:00, the battery charges and slightly increases feeder demand
The effect is applied by modifying feeder_mult, which scales the baseline feeder load.
________________________________________

Meaning of levels
Battery = 33
•	evening feeder load reduced by 4%
•	midday feeder load increased by 1%
Interpretation:
•	small battery deployment
•	modest peak shaving capability
•	limited support to the feeder
Battery = 66
•	evening feeder load reduced by 8%
•	midday feeder load increased by 2%
Interpretation:
•	medium battery deployment
•	meaningful peak shaving
•	stronger reduction of overload and voltage stress
Battery = 100
•	evening feeder load reduced by 12%
•	midday feeder load increased by 3%
Interpretation:
•	large or aggressive battery support
•	substantial peak shaving
•	strongest battery-based mitigation among modeled levels
________________________________________
Practical intuition
Higher battery levels represent:
•	greater storage capacity
•	stronger dispatch capability
•	more ability to reduce evening feeder stress
The midday charge increase is smaller than the evening discharge reduction, reflecting the planning assumption that charging happens when the system is under less stress.
________________________________________
 
2. Managed Charging
What managed charging represents
Managed charging represents utility, aggregator, or programmatic control of EV charging behavior. Instead of allowing all EV charging to occur during the natural evening peak, some charging is shifted to late-night hours.
This is one of the most important non-wires alternatives in EV-driven scenarios because unmanaged charging often aligns with system peak and drives overloads.
Managed charging can:
•	reduce evening peak demand
•	reduce transformer and line overload
•	improve minimum voltages in high-demand hours
•	flatten the daily load profile
________________________________________
How is it implemented:
•	some portion of EV charging energy is removed from 18:00–21:00
•	that removed energy is redistributed evenly across 00:00–05:00
The intervention conserves EV charging energy overall, but changes its timing.
________________________________________
Meaning of levels
ManagedCharging = 33
•	15% of evening EV charging is shifted to late-night hours
Interpretation:
•	low customer participation or limited control capability
•	modest peak relief
ManagedCharging = 66
•	30% of evening EV charging is shifted
Interpretation:
•	moderate participation or stronger control signals
•	meaningful reduction of EV-driven peak
ManagedCharging = 100
•	50% of evening EV charging is shifted
Interpretation:
•	high participation or aggressive managed charging program
•	largest modeled EV peak reduction
________________________________________
Practical intuition
Higher levels represent:
•	more EV customers enrolled
•	stronger utility or aggregator control
•	better communications/control coverage
•	stronger customer response
This intervention directly targets EV-caused evening stress.
________________________________________
 
3. Phased Interconnection
What phased interconnection represents
Phased interconnection represents a staged energization of a new large load, such as a data center. Instead of connecting the full load immediately, only a portion becomes active in the planning period.
This is a realistic planning alternative where:
•	the utility cannot serve the full load immediately without upgrades
•	the customer agrees to phased load ramp-up
•	grid reinforcement is deferred or staged
This is particularly useful in scenarios with large new demand from data centers or industrial customers.

________________________________________
Meaning of levels
Phased Interconnection = 33
•	data center load reduced by 20%
Interpretation:
•	mild phasing
•	most of the load still connects, but part is deferred
Phased Interconnection = 66
•	data center load reduced by 40%
Interpretation:
•	moderate phasing
•	significant part of data center ramp is deferred
Phased Interconnection = 100
•	data center load reduced by 60%
Interpretation:
•	aggressive phasing
•	majority of near-term data center demand is deferred
________________________________________
Practical intuition
Higher levels represent:
•	stronger customer agreement to defer energization
•	slower commissioning of data hall capacity
•	reduced near-term feeder stress
This intervention is especially valuable when one large customer dominates the overload problem.
________________________________________
4. Demand Tariff
What demand tariff represents
Demand tariff represents the effect of a tariff or price-based demand management program that reduces peak consumption. It is modeled as a reduction in:
•	general feeder demand during peak hours
•	EV charging demand during peak hours
This reflects the idea that price signals or demand charges can encourage customers to reduce or shift demand away from high-stress hours.
________________________________________
How is it implemented:
•	during 17:00–20:00, overall feeder demand is reduced by a percentage
________________________________________
Meaning of levels
DemandTariff = 33
•	feeder demand reduced by 3%
Interpretation:
•	weak tariff signal
•	modest customer response
DemandTariff = 66
•	feeder demand reduced by 6%
Interpretation:
•	moderate tariff effectiveness
•	stronger response from flexible loads
DemandTariff = 100
•	feeder demand reduced by 10%
Interpretation:
•	strong tariff signal
•	highest modeled customer demand reduction
________________________________________
Practical intuition
Higher levels represent:
•	more effective tariff design
•	stronger customer responsiveness
•	larger peak shaving from demand response behavior
This intervention is useful where customer elasticity exists, especially in EV-heavy or flexible-load scenarios.
________________________________________
 
5. Transformer Upgrade
What transformer upgrade represents
Transformer upgrade represents a conventional wired solution that increases network thermal capacity. In the current prototype, this is not modeled by editing a specific transformer asset directly. Instead, it is represented by increasing the effective allowable loading limits used when determining overloads.
This is a planning abstraction for:
•	replacing transformers with larger units
•	reinforcing equipment
•	increasing feeder thermal headroom
It is treated as a network reinforcement measure.
________________________________________
How is it implemented:
•	transformer upgrade increases effective transformer capacity
•	it also provides some effective line capacity benefit in the model
________________________________________
Meaning of levels
TransformerUpgrade = 33
•	transformer capacity multiplied by 1.10
•	line capacity multiplied by 1.08
Interpretation:
•	small or selective reinforcement
•	modest additional headroom
TransformerUpgrade = 66
•	transformer capacity multiplied by 1.20
•	line capacity multiplied by 1.15
Interpretation:
•	medium reinforcement
•	meaningful increase in thermal capability
TransformerUpgrade = 100
•	transformer capacity multiplied by 1.30
•	line capacity multiplied by 1.25
Interpretation:
•	large/full reinforcement effect
•	strongest capacity increase among modeled levels
________________________________________
Practical intuition
Higher levels represent:
•	larger equipment replacement
•	stronger conventional reinforcement
•	greater reduction in overload risk through added infrastructure capacity
Unlike the non-wires alternatives, transformer upgrade does not reduce demand. Instead, it increases the system’s ability to serve the demand.

