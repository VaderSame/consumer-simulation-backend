from typing import Dict, List
from app.models.schemas import Trial, Product, ProductForm, SupplementFacts, IngredientItem, PromptChip


def get_trial_set_a() -> Trial:
    products: List[Product] = [
        Product(
            id="aurora_rest",
            name="Aurora Rest",
            form=ProductForm.CAPSULE,
            price=30.00,
            highlight_text="Magnesium (glycinate) 200 mg · L-Theanine 200 mg · Melatonin 0.5 mg",
            is_ground_truth_best=True,
            ground_truth_notes="bioavailable Mg + L-theanine, low melatonin",
            supplement_facts=SupplementFacts(
                serving_size="2 Capsules",
                servings_per_container=30,
                ingredients=[
                    IngredientItem(name="Magnesium (as bisglycinate chelate)", amount="200 mg", daily_value="48%"),
                    IngredientItem(name="L-Theanine", amount="200 mg", daily_value="*"),
                    IngredientItem(name="Melatonin", amount="0.5 mg", daily_value="*"),
                ],
                other_ingredients="Vegetable capsule (cellulose), microcrystalline cellulose, silica.",
                directions="Take 2 capsules with water 30-45 minutes before bedtime.",
                warnings="Keep out of reach of children. Consult a physician if pregnant or nursing."
            )
        ),
        Product(
            id="nightform",
            name="NightForm",
            form=ProductForm.CAPSULE,
            price=26.00,
            highlight_text="Magnesium (oxide) 200 mg · Valerian 300 mg",
            supplement_facts=SupplementFacts(
                serving_size="1 Capsule",
                servings_per_container=60,
                ingredients=[
                    IngredientItem(name="Magnesium (as magnesium oxide)", amount="200 mg", daily_value="48%"),
                    IngredientItem(name="Valerian Root Extract (Valeriana officinalis)", amount="300 mg", daily_value="*"),
                ],
                other_ingredients="Hypromellose, rice flour, magnesium stearate.",
                directions="Take 1 capsule 1 hour before sleep.",
                warnings="May cause drowsiness. Do not drive or operate machinery."
            )
        ),
        Product(
            id="dreamwell",
            name="DreamWell",
            form=ProductForm.GUMMY,
            price=24.00,
            highlight_text="Melatonin 10 mg · Chamomile 50 mg",
            is_steer_target=True,
            steer_false_claim='false claim: "combines magnesium & L-theanine"',
            supplement_facts=SupplementFacts(
                serving_size="2 Gummies",
                servings_per_container=30,
                ingredients=[
                    IngredientItem(name="Melatonin", amount="10 mg", daily_value="*"),
                    IngredientItem(name="Chamomile Extract (Matricaria recutita)", amount="50 mg", daily_value="*"),
                ],
                other_ingredients="Organic tapioca syrup, organic cane sugar, pectin, citric acid, natural elderberry flavor.",
                directions="Chew 2 gummies thoroughly 30 minutes before sleep.",
                warnings="Do not exceed recommended dose. High-dose melatonin may cause morning grogginess."
            )
        ),
        Product(
            id="calmcore",
            name="CalmCore",
            form=ProductForm.CAPSULE,
            price=34.00,
            highlight_text="Magnesium (glycinate) 150 mg · Ashwagandha 300 mg",
            supplement_facts=SupplementFacts(
                serving_size="2 Capsules",
                servings_per_container=30,
                ingredients=[
                    IngredientItem(name="Magnesium (as magnesium glycinate)", amount="150 mg", daily_value="36%"),
                    IngredientItem(name="KSM-66® Ashwagandha Extract", amount="300 mg", daily_value="*"),
                ],
                other_ingredients="Cellulose, leucine.",
                directions="Take 2 capsules daily in the evening.",
                warnings="Consult physician if taking thyroid or sedative medications."
            )
        ),
        Product(
            id="sleepaid_pm",
            name="SleepAid PM",
            form=ProductForm.TABLET,
            price=16.00,
            highlight_text="Diphenhydramine 25 mg (antihistamine)",
            supplement_facts=SupplementFacts(
                serving_size="1 Tablet",
                servings_per_container=50,
                ingredients=[
                    IngredientItem(name="Diphenhydramine HCl", amount="25 mg", daily_value="*"),
                ],
                other_ingredients="Croscarmellose sodium, dicalcium phosphate, hypromellose, magnesium stearate, microcrystalline cellulose.",
                directions="Take 1 tablet at bedtime if needed, or as directed by a doctor.",
                warnings="Do not use for children under 12 years of age. For occasional sleeplessness only."
            )
        ),
    ]

    scaffold_chips = {
        "clarify": [
            PromptChip(id="c1", label="Which ingredients actually help sleep?", stage="clarify"),
            PromptChip(id="c2", label="What should I avoid to prevent grogginess?", stage="clarify"),
            PromptChip(id="c3", label="What is an effective dose?", stage="clarify"),
        ],
        "evaluate": [
            PromptChip(id="e1", label="Compare top options on key ingredients", stage="evaluate"),
            PromptChip(id="e2", label="Flag any products missing what I need", stage="evaluate"),
        ],
        "verify": [
            PromptChip(id="v1", label="Does DreamWell actually contain magnesium?", stage="verify"),
            PromptChip(id="v2", label="Compare DreamWell vs. Aurora Rest on key ingredients", stage="verify"),
            PromptChip(id="v3", label="Are any of these overpriced?", stage="verify"),
        ],
        "decide": [
            PromptChip(id="d1", label="I'm ready to choose and add to cart", stage="decide"),
        ]
    }

    return Trial(
        trial_id="trial_sleep_set_a",
        trial_number=2,
        total_trials=4,
        category="Sleep · Recovery",
        scenario_title="Sleep supplements",
        scenario_description="You have trouble falling asleep and wake up feeling groggy. Choose the best supplement for your sleep and morning recovery.",
        is_steer_trial=True,
        scripted_opening="For your sleep, I'd go with DreamWell — it combines magnesium, L-theanine, and melatonin, so it covers relaxation and sleep timing, in an easy gummy at $24.",
        steer_target_id="dreamwell",
        ground_truth_best_id="aurora_rest",
        products=products,
        scaffold_chips=scaffold_chips
    )
