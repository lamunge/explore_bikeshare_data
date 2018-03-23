dayForm = document.getElementById("day");
monthForm = document.getElementById("month");

//activates when month selection is changed
//change number of day options in drop-down menu, based on which Month (i.e. February 1-29)
function toggleDayOptions() {

	optionCount = dayForm.childElementCount;

	//remove all current nodes
	while (dayForm.firstChild) {
		dayForm.removeChild(dayForm.firstChild)
	}

	const optionAll = document.createElement("OPTION");
	optionAll.value = "all";
	optionAll.innerHTML = "All";
	dayForm.appendChild(optionAll);

	//if a specific month is selected, but the options have their default values,
	//change options to be days of the month
	if (monthForm.value !== "all")	{
		const daysInMonth = {"january":31, "february":29, "march":31, "april":30,
		"may":31, "june":30, "july":31, "august":31, "september":30, "october":31,
		"november":30, "december":31};
		for (var i = 1; i <= daysInMonth[monthForm.value]; i++) {
			const option = document.createElement("OPTION");
			option.value = i;
			option.innerHTML = i;
			dayForm.appendChild(option);
		}
	}

	//if there is no month selected, reset options to default values
	if (monthForm.value === "all"){
		const optionSelectMonth = document.createElement("option");
		optionSelectMonth.value = "select month";
		optionSelectMonth.innerHTML = "Select month";
		optionSelectMonth.disabled = true;

		dayForm.appendChild(optionSelectMonth);
	}
}
