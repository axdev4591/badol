const usernameField =  document.querySelector('#id_username');
const feedbackArea =  document.querySelector('.invalid-feedback');//put a dot when it's a class and # when id
const emailField =  document.querySelector('#id_email');
const emailFeedbackArea =  document.querySelector('.emailFeedbackArea');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const useremailSuccessOutput = document.querySelector('.useremailSuccessOutput');
const showPasswordToggle =  document.querySelector('.showPasswordToggle');
const passwordField =  document.querySelector('#id_password');
const submitBtn =  document.querySelector('.submit-btn');


//Username validation event
usernameField.addEventListener('keyup', (e)=> {

    const usernameVal = e.target.value;

    //reset the field to empty value
    usernameField.classList.remove("is-invalid");
    feedbackArea.style.display = 'none';
    usernameSuccessOutput.style.display = 'none';
    usernameSuccessOutput.textContent = `Checking ${usernameVal}`;


    //Create a fetch API, allow us to do what we do with Postman just in Javascript
    if(usernameVal.length > 0){

        fetch('/authentication/validate-username', {

            //we specify in the body what we are sending (data in Json), the method used POST
            body: JSON.stringify({ username:  usernameVal }), //here we convert a JS object into a correct JSON
            method: "POST", 

        }).then((res) => res.json()) //first then, convert the response to Json, and second return data
          .then((data) =>{ 
            console.log('data: ', data);
            usernameSuccessOutput.style.display = 'block';
            if(data.username_error){
                usernameField.classList.add("is-invalid");
                feedbackArea.style.display = 'block';
                feedbackArea.innerHTML =  `<p>${data.username_error}</p>`;
                submitBtn.disabled = true;

            }else{
                submitBtn.removeAttribute('disabled');

            }
        });
    }
   
});


//email validation event
emailField.addEventListener('keyup', (e)=> {

    const emailVal = e.target.value;

    emailField.classList.remove("is-invalid");
    emailFeedbackArea.style.display = 'none';

    useremailSuccessOutput.style.display = 'none';
    useremailSuccessOutput.textContent = `Checking ${emailVal}`;


    if(emailVal.length > 0){

        fetch('/authentication/validate-email', {

            body: JSON.stringify({ email:  emailVal }),
            method: "POST", 

        }).then((res) => res.json())
          .then((data) =>{ 
            console.log('object', data);
            if(data.email_error){
                submitBtn.disabled = true;
                useremailSuccessOutput.style.display = 'block';
                emailField.classList.add("is-invalid");
                emailFeedbackArea.style.display = 'block';
                emailFeedbackArea.innerHTML =  `<p>${data.email_error}</p>`;
            }else{
                submitBtn.removeAttribute('disabled');

            }
        });
    }
   

});

//passord toggle
const handleToggleInput = (e) => {

    if(showPasswordToggle.textContent=="SHOW"){
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    }else{
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");

    }
};
showPasswordToggle.addEventListener('click', handleToggleInput);
