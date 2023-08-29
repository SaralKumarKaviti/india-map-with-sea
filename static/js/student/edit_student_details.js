// Your provided JavaScript code starts here
const ecardContent = document.querySelector('.ecard-content');

let totalExperienceEntries = 0;
function addExperienceData() {

  totalExperienceEntries++;
  document.getElementById('totalExperienceEntries').value = totalExperienceEntries;

  let inputGroup = document.createElement('div');
  inputGroup.className = 'form-group';

  let flexContainer = document.createElement('div');
  flexContainer.className = 'd-flex'; // Use Bootstrap class for flex container

  // Create the Company Name label and input
  let companyContainer = document.createElement('div');
  companyContainer.className = 'flex-grow-1'; // Use Bootstrap class for flex item

  let company = document.createElement('label');
  company.textContent = 'Company Name';

  let companyInput = document.createElement('input');
  companyInput.type = 'text';
  companyInput.className = 'form-control';
  companyInput.placeholder = 'Enter company name';
  companyInput.name = 'companyName'+totalExperienceEntries;

  companyContainer.appendChild(company);
  companyContainer.appendChild(companyInput);

  // Create the Role label and input
  let roleContainer = document.createElement('div');
  roleContainer.className = 'flex-grow-1'; // Use Bootstrap class for flex item

  let role = document.createElement('label');
  role.textContent = 'Role';

  let roleInput = document.createElement('input');
  roleInput.type = 'text';
  roleInput.className = 'form-control';
  roleInput.placeholder = 'Enter role';
  roleInput.name = 'role'+totalExperienceEntries;

  roleContainer.appendChild(role);
  roleContainer.appendChild(roleInput);

  // Create the From Year label and select
  let fromYearContainer = document.createElement('div');
  fromYearContainer.className = 'flex-grow-1'; // Use Bootstrap class for flex item

  let fromYearLabel = document.createElement('label');
  fromYearLabel.textContent = 'From Year';

  let fromYearSelect = document.createElement('select');
  fromYearSelect.className = 'form-control';
  fromYearSelect.name = 'fromYear'+totalExperienceEntries;

  for (let year = 2023; year >= 1990; year--) {
    let option = document.createElement('option');
    option.value = year;
    option.textContent = year;
    fromYearSelect.appendChild(option);
  }

  fromYearContainer.appendChild(fromYearLabel);
  fromYearContainer.appendChild(fromYearSelect);

  let toYearContainer = document.createElement('div');
  toYearContainer.className = 'flex-grow-1'; // Use Bootstrap class for flex item

  let toYearLabel = document.createElement('label');
  toYearLabel.textContent = 'To Year';

  let toYearSelect = document.createElement('select');
  toYearSelect.className = 'form-control';
  toYearSelect.name = 'toYear'+totalExperienceEntries;

  for (let year = 2023; year >= 1990; year--) {
    let option = document.createElement('option');
    option.value = year;
    option.textContent = year;
    toYearSelect.appendChild(option);
  }

  toYearContainer.appendChild(toYearLabel);
  toYearContainer.appendChild(toYearSelect);


  flexContainer.appendChild(companyContainer);
  flexContainer.appendChild(roleContainer);
  flexContainer.appendChild(fromYearContainer);
  flexContainer.appendChild(toYearContainer);

  

  inputGroup.appendChild(flexContainer);

  // Create the Project Description label and textarea
  let projectDescContainer = document.createElement('div');
  projectDescContainer.className = 'form-group';

  let projectDescLabel = document.createElement('label');
  projectDescLabel.textContent = 'Project Description';

  let projectDescTextarea = document.createElement('textarea');
  projectDescTextarea.className = 'form-control';
  projectDescTextarea.placeholder = 'Enter project description';
  projectDescTextarea.rows = '3'; // Set number of rows
  projectDescTextarea.name = "projectDesc"+totalExperienceEntries;

  projectDescContainer.appendChild(projectDescLabel);
  projectDescContainer.appendChild(projectDescTextarea);

  
  let deleteButton = document.createElement('button');
  deleteButton.className = 'btn btn-danger ml-3'; // Use Bootstrap classes for button styling
  deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>'; // FontAwesome trash icon

  deleteButton.style.padding = '5px 10px'; // Adjust padding
  deleteButton.style.borderRadius = '50%'; // Make it circular
  deleteButton.style.marginRight = 'auto';

  // Add event listener to delete the input group on click
  deleteButton.addEventListener('click', () => {
    inputGroup.remove(); 
  });

  inputGroup.appendChild(projectDescContainer);
  inputGroup.appendChild(deleteButton);

  ecardContent.appendChild(inputGroup);
}

// const scardContent = document.querySelector('.scard-content');
// let totalskills = 0;

// function addSkills() {
//   totalskills++;
//   document.getElementById('totalskills').value = totalskills;

//   let skillGroup = document.createElement('div');
//   skillGroup.className = 'form-group';

//   let skillContainer = document.createElement('div');
//   skillContainer.className = 'd-flex';

//   let technologyContainer = document.createElement('div');
//   technologyContainer.className = 'flex-grow-1';

//   let technology = document.createElement('label');
//   technology.textContent = 'Technology Name';

//   let technologyInput = document.createElement('input');
//   technologyInput.type = 'text';
//   technologyInput.className = 'form-control';
//   technologyInput.placeholder = 'Technology name';
//   technologyInput.name = 'technologyName' + totalskills;

//   technologyContainer.appendChild(technology);
//   technologyContainer.appendChild(technologyInput);

//   let skillLevelContainer = document.createElement('div');
//   skillLevelContainer.className = 'flex-grow-1';

//   let skillLevelLabel = document.createElement('label');
//   skillLevelLabel.textContent = 'Skill Level';

//   let skillLevelSelect = document.createElement('select');
//   skillLevelSelect.className = 'form-control';
//   skillLevelSelect.name = 'skillLevel' + totalskills;

//   let skillLevels = ['Beginner', 'Intermediate', 'Advanced', 'Professional', 'Master'];
//   for (let level of skillLevels) {
//     let option = document.createElement('option');
//     option.value = level;
//     option.textContent = level;
//     skillLevelSelect.appendChild(option);
//   }

//   skillLevelContainer.appendChild(skillLevelLabel);
//   skillLevelContainer.appendChild(skillLevelSelect);

//   skillContainer.appendChild(technologyContainer);
//   skillContainer.appendChild(skillLevelContainer);

//   skillGroup.appendChild(skillContainer);

//   let skillDeleteButton = document.createElement('button');
//   skillDeleteButton.className = 'btn btn-danger ml-3';
//   skillDeleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
//   skillDeleteButton.style.padding = '5px 10px';
//   skillDeleteButton.style.borderRadius = '50%';
//   skillDeleteButton.style.marginRight = 'auto';

//   skillDeleteButton.addEventListener('click', () => {
//     skillGroup.remove();
//   });

//   skillGroup.appendChild(skillDeleteButton);

//   scardContent.appendChild(skillGroup);
// }

// const smcardContent = document.querySelector('.social-media-fields');

// let totalMedia = 0;

// function addSocialMediaInput() {
//   totalMedia++;
//   document.getElementById('totalMedia').value = totalMedia;

//   let smGroup = document.createElement('div');
//   smGroup.className = 'form-group d-flex align-items-center'; // Use d-flex and align-items-center classes

//   // Create the Social Media label and input
//   let smLabel = document.createElement('label');
//   smLabel.textContent = 'Social Media';
//   smLabel.className = 'flex-grow-1'; // Use Bootstrap class for flex item

//   let smInput = document.createElement('input');
//   smInput.type = 'text';
//   smInput.className = 'form-control';
//   smInput.placeholder = 'Enter social media';
//   smInput.name = 'socialMedia' + totalMedia;

//   smLabel.appendChild(smInput);
//   smGroup.appendChild(smLabel);

//   // Create the Social Media URL label and input
//   let smlLabel = document.createElement('label');
//   smlLabel.textContent = 'Social Media URL';
//   smlLabel.className = 'flex-grow-1'; // Use Bootstrap class for flex item

//   let smlInput = document.createElement('input');
//   smlInput.type = 'text';
//   smlInput.className = 'form-control';
//   smlInput.placeholder = 'Enter social media URL';
//   smlInput.name = 'socialMediaURL' + totalMedia;

//   smlLabel.appendChild(smlInput);
//   smGroup.appendChild(smlLabel);

//   let deleteButton = document.createElement('button');
//   deleteButton.className = 'btn btn-danger ml-3';
//   deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
//   deleteButton.style.padding = '5px 10px';
//   deleteButton.style.borderRadius = '50%';
//   deleteButton.style.marginRight = 'auto';
//   deleteButton.addEventListener('click', () => {
//     smGroup.remove();
//   });

//   smGroup.appendChild(deleteButton);

//   smcardContent.appendChild(smGroup);
// }

// const pincodeInput = document.getElementById('pincodeInput');
// const stateInput = document.getElementById('stateInput');
// const districtInput = document.getElementById('districtInput');
// const mandalInput = document.getElementById('mandalInput');
// const villageInput = document.getElementById('villageInput');

// // Add event listener to the pincode input field
// pincodeInput.addEventListener('input', async () => {
//   const pincode = pincodeInput.value;

//   if (pincode.length === 6) {
//     const response = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
//     const data = await response.json();

//     if (data[0]['Status'] === 'Success') {
//       const details = data[0]['PostOffice'][0];
//       stateInput.value = details['State'];
//       districtInput.value = details['District'];
//       mandalInput.value = details['Block'];
//       villageInput.value = details['Name'];
//     } else {
//       // Clear the fields if pincode is not found
//       stateInput.value = '';
//       districtInput.value = '';
//       mandalInput.value = '';
//       villageInput.value = '';
//     }
//   }
// });
// function validateForm() {
//     var profilePicInput = document.getElementById('fileInput');
//     var pincodeInput = document.getElementById('pincodeInput');

//     // Check if the logout button is clicked and skip validation
//     if (profilePicInput && profilePicInput.value && profilePicInput.closest('form').contains(event.target)) {
//       return true; // Allow form submission for logout button
//     }

//     if (profilePicInput && !profilePicInput.value) {
//       alert("Profile picture file should be uploaded.");
//       return false; // Prevent form submission for other cases
//     }

//     if (!pincodeInput.value) {
//       alert("Please enter the pincode.");
//       return false; // Prevent form submission
//     }

//     // If all required fields are valid, show success alert
//     alert("Data submitted successfully!");
//     return true; // Allow form submission
//   }