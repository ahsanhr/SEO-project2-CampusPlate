const buildPlateButton = document.getElementById('build-plate-button');
buildPlateButton.addEventListener('click', async () => {
    const requestPayload = {
        user_id: 1,
        meal_type: 'lunch', 
        max_items: 5,
        num_combos: 4
    };

    try {
        const response = await fetch('/proxy/5000/api/v1/generate-plate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                
            },
            body: JSON.stringify(requestPayload)
        });
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        const data = await response.json();
        renderMeals(data.meals);
    } catch (error) {
        console.error('Failed to generate plate:', error);
    }
});


function renderMeals(meals){
    const container = document.getElementById('meal-output-container');
    container.innerHTML = '';
    console.log(meals)
    meals.forEach((meal, index) => {
        container.innerHTML += `
            <div class="card mb-3">
                <div class="card-body">
                    <h5>Option ${index + 1}</h5>
                    <p>${meal.foods[0].name} | ${meal.foods[1].name} | ${meal.foods[2].name} </p>
                    <p>${meal.totals.calories} kcal | ${meal.totals.protein}g Protein</p>
                </div>
            </div>
        `;
    });
}

