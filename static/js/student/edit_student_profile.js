function addExperience() {
    var experienceContainer = document.getElementById('experienceContainer');
    
    var experienceDiv = document.createElement('div');
    var index = experienceContainer.childElementCount; // Calculate the index
    
    experienceDiv.id = 'experienceDiv' + index;
    experienceDiv.className = 'ecard-content';
    
    // Create HTML elements for each input field
    var companyNameInput = createInput('Company Name', 'editedCompanyName');
    var roleInput = createInput('Role', 'editedRole');
    var fromYearInput = createInput('From Year', 'editedFromYear');
    var toYearInput = createInput('To Year', 'editedToYear');
    var projectDescTextarea = createTextarea('Project Description', 'editedProjectDesc');
    
    // Append input fields to the experience detail section
    experienceDiv.appendChild(companyNameInput);
    experienceDiv.appendChild(roleInput);
    experienceDiv.appendChild(fromYearInput);
    experienceDiv.appendChild(toYearInput);
    experienceDiv.appendChild(projectDescTextarea);
    
    // Append the experience detail section to the container
    experienceContainer.appendChild(experienceDiv);
}

// Function to remove the last experience detail section
function removeExperience() {
    var experienceContainer = document.getElementById('experienceContainer');
    if (experienceContainer.childElementCount > 0) {
        experienceContainer.removeChild(experienceContainer.lastChild);
    }
}

// Helper function to create an input element
function createInput(placeholder, name) {
    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control';
    input.name = name + (experienceContainer.childElementCount + 1);
    input.placeholder = placeholder;
    return input;
}

// Helper function to create a textarea element
function createTextarea(placeholder, name) {
    var textarea = document.createElement('textarea');
    textarea.className = 'form-control';
    textarea.rows = '4';
    textarea.name = name + (experienceContainer.childElementCount + 1);
    textarea.placeholder = placeholder;
    return textarea;
}


const smcardContent = document.querySelector('.social-media-fields');

function addSocialMediaInput() {
  totalMediaEntries++; // Increment the count
  document.getElementById('editedTotalMedia').value = totalMediaEntries;

  let formGroup = document.createElement('div');
  formGroup.className = 'form-group';

  let label = document.createElement('label');
  label.textContent = 'Social Media ' + totalMediaEntries + ':';

  let input = document.createElement('input');
  input.type = 'text';
  input.className = 'form-control';
  input.placeholder = 'Enter social media';
  input.name = 'editedSocialMedia' + totalMediaEntries;

  let urlLabel = document.createElement('label');
  urlLabel.textContent = 'Social Media URL ' + totalMediaEntries + ':';

  let urlInput = document.createElement('input');
  urlInput.type = 'text';
  urlInput.className = 'form-control';
  urlInput.placeholder = 'Enter social media URL';
  urlInput.name = 'editedSocialMediaURL' + totalMediaEntries;

  formGroup.appendChild(label);
  formGroup.appendChild(input);
  formGroup.appendChild(urlLabel);
  formGroup.appendChild(urlInput);

  smcardContent.appendChild(formGroup);
}

const pincodeInput = document.getElementById('pincodeInput');
const stateInput = document.getElementById('stateInput');
const districtInput = document.getElementById('districtInput');
const mandalInput = document.getElementById('mandalInput');
const villageInput = document.getElementById('villageInput');

// Add event listener to the pincode input field
pincodeInput.addEventListener('input', async () => {
  const pincode = pincodeInput.value;

  if (pincode.length === 6) {
    const response = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
    const data = await response.json();

    if (data[0]['Status'] === 'Success') {
      const details = data[0]['PostOffice'][0];
      stateInput.value = details['State'];
      districtInput.value = details['District'];
      mandalInput.value = details['Block'];
      villageInput.value = details['Name'];
    } else {
      // Clear the fields if pincode is not found
      stateInput.value = '';
      districtInput.value = '';
      mandalInput.value = '';
      villageInput.value = '';
    }
  }
});