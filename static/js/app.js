const buildPlateButton = document.getElementById('build-plate-button');
if (buildPlateButton) {
    buildPlateButton.addEventListener('click', async () => {
        const selectedMeal = document.getElementById('meal-type').value;

        const requestPayload = {
            meal_type: selectedMeal, 
            max_items: 5,
            num_combos: 4
        };

        const token = localStorage.getItem('jwt_token');
        if (!token) throw new Error("No token found");

        try {
            const response = await fetch('/api/v1/generate-plate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(requestPayload)
            });
            if (!response.ok) {
                throw new Error(data.error || `Server error: ${response.status}`);
            }
            const data = await response.json();

            renderMeals(data.meals);
        } catch (error) {
            console.error('Failed to generate plate:', error);
        }
    });
}

function renderMeals(meals){
    const container = document.getElementById('meal-output-container');
    container.innerHTML = '';
    console.log(meals)
    meals.forEach((meal, index) => {
        const foodNames = meal.foods.map(food => food.name).join(' | ');
        container.innerHTML += `
            <div class="card mb-3">
                <div class="card-body">
                    <h5>Option ${index + 1}</h5>
                    <p>${foodNames} </p>
                    <p>${meal.totals.calories} kcal | ${meal.totals.protein}g Protein</p>
                </div>
            </div>
        `;
    });
}
const signUpButton = document.getElementById('sign-up-button');
if(signUpButton) {
    signUpButton.addEventListener('click', async (e) => {
        e.preventDefault()

        const createUser = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
        }

        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',

                },
                body: JSON.stringify(createUser)
            });
            if(!response.ok) {
                throw new Error(`Server Error: ${response.status}`)
            }
            const data = await response.json()
            localStorage.setItem('jwt_token', data.token);
            window.location.href = '/account';
        } catch (error) {
            console.error(`failed Sign Up: ${error}`);
        }
    });
}

const loginButton = document.getElementById('login-button');
if(loginButton){
    loginButton.addEventListener('click', async (e) => {

        e.preventDefault()

        const existingUser = {
            email: document.getElementById('login-email').value,
            password: document.getElementById('login-password').value,
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',

                },
                body: JSON.stringify(existingUser)
            });
            if(!response.ok) {
                throw new Error(`Server Error: ${response.status}`)
            }
            const data = await response.json()
            localStorage.setItem('jwt_token', data.token);
            window.location.href = '/account';
        } catch (error) {
            console.error(`failed Sign Up: ${error}`);
        }
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const token = localStorage.getItem('jwt_token')

        if (!token) throw new Error("No token found");

        const auth = await fetch('/api/auth/me', {
            method: 'GET',
            headers: {"Authorization" : `Bearer ${token}`}
        });

        const profile = await auth.json();


        if (!auth.ok) {
            throw new Error(profile.error);
        }

        const nameDisplay = document.getElementById('username-display');
        if (nameDisplay) nameDisplay.innerText = profile.username;

        const goalsForm = document.getElementById('goals-form');
        if (goalsForm) {
            try {
                goals = await fetch('/api/goals', {
                    method: 'GET',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                goalsData = await goals.json();

                if (goalsData.has_goals){
                    document.getElementById('user-calories-display').innerText = goalsData.calories;
                    document.getElementById('user-protein-display').innerText = goalsData.protein_g;
                    document.getElementById('user-fats-display').innerText = goalsData.fat_g;
                    document.getElementById('user-carbs-display').innerText = goalsData.carbs_g;
                    
                    document.getElementById('goal-calories').value = goalsData.calories;
                    document.getElementById('goal-protein').value = goalsData.protein_g;
                    document.getElementById('goal-fats').value = goalsData.fat_g;
                    document.getElementById('goal-carbs').value = goalsData.carbs_g;
                }
            } catch (error) {
                console.error(`could not fetch goals: ${error}`);
            }
            const methodDropdown = document.getElementById('select-method');
            const directSection = document.getElementById('direct-form');
            const calcSection = document.getElementById('calculate-form');

            if (methodDropdown && directSection && calcSection) {
                methodDropdown.addEventListener('change', (e) => {
                    if (e.target.value === 'direct') {
                        directSection.style.display = 'block';
                        calcSection.style.display = 'none';
                    } else {
                        directSection.style.display = 'none';
                        calcSection.style.display = 'block';
                    }
                });
            }
            const goalsButton = document.getElementById('submit-goals-button');
            if(goalsButton){
                goalsButton.addEventListener('click', async (e) => {
                    e.preventDefault(); 

                    const isDirect = methodDropdown.value === 'direct';
                    let endpoint = '';
                    let payload = {};

                    if (isDirect) {
                        endpoint = '/api/goals/direct';
                        payload = {
                            calories: parseFloat(document.getElementById('goal-calories').value),
                            protein_g: parseFloat(document.getElementById('goal-protein').value),
                            fat_g: parseFloat(document.getElementById('goal-fats').value),
                            carbs_g: parseFloat(document.getElementById('goal-carbs').value)
                        };
                    } else {
                        endpoint = '/api/goals/calculated';
                        payload = {
                            age: parseInt(document.getElementById('calc-age').value),
                            height: parseFloat(document.getElementById('calc-height').value),
                            weight: parseFloat(document.getElementById('calc-weight').value),
                            sex: document.getElementById('calc-sex').value, 
                            activity: document.getElementById('calc-activity').value,
                            fitness_goal: document.getElementById('calc-goal').value
                        };
                    }

                    try {
                        const saveResponse = await fetch(endpoint, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`
                            },
                            body: JSON.stringify(payload)
                        });

                        const saveData = await saveResponse.json();

                        if (!saveResponse.ok) {
                            throw new Error(saveData.error || 'Failed to save goals');
                        }

                        document.getElementById('user-calories-display').innerText = saveData.goals.calories;
                        document.getElementById('user-protein-display').innerText = saveData.goals.protein_g;
                        document.getElementById('user-fats-display').innerText = saveData.goals.fat_g;
                        document.getElementById('user-carbs-display').innerText = saveData.goals.carbs_g;
                        

                    } catch (error) {
                        console.error("Submission error:", error);
                    }
                });
            }
        }
    } catch (error){
        console.error(error);
    }
});