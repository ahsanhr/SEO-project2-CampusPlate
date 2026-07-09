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
            const response = await fetch('/proxy/5000/api/v1/generate-plate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
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
}

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
const signUpButton = document.getElementById('sign-up-button');
if(signUpButton) {
    signUpButton.addEventListener('click', async() => {
        const createUser = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
        }

        try {
            const response = await fetch('/proxy/5000/api/auth/signup', {
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
    loginButton.addEventListener('click', async() => {
        const existingUser = {
            email: document.getElementById('login-email').value,
            password: document.getElementById('login-password').value,
        }

        try {
            const response = await fetch('/proxy/5000/api/auth/login', {
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
            window.location.href = '/proxy/5000/account';
        } catch (error) {
            console.error(`failed Sign Up: ${error}`);
        }
    });
}

document.addEventListener('DOMContentLoaded', async () => {

    try {
        const token = localStorage.getItem('jwt_token');
        if (!token) throw new Error("No token found");

        const response = await fetch('/proxy/5000/api/auth/me', {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const profileData = await response.json();
        
        if (!response.ok) {
            localStorage.removeItem('jwt_token'); 
            throw new Error(profileData.error);
        }
        const nameDisplay = document.getElementById('username-display');
        const welcomeHeading = document.getElementById('welcome-heading');
        const loadingMsg = document.getElementById('loading-message');

        if (nameDisplay) nameDisplay.innerText = profileData.username;
        if (welcomeHeading) welcomeHeading.style.display = 'block';
        if (loadingMsg) loadingMsg.style.display = 'none';

    } catch (error) {
            console.log("status:", error.message);
        }
});
