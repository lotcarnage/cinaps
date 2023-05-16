class CalendarUI {
	static #getToday() {
		let now = new Date(Date.now());
		let today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		return today;
	}
	constructor(parent, select_day_callback = null) {
		const week_day_class = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
		const week_day_name = ["日", "月", "火", "水", "木", "金", "土"];
		this.frame = document.createElement("div");
		this.frame.className = "CalendarUI";
		let header = document.createElement("div");
		let left_button = document.createElement("span");
		let right_button = document.createElement("span");
		let year_month_view = document.createElement("span");
		left_button.className = "button left_button";
		year_month_view.innerText = "2023年1月";
		right_button.className = "button right_button";
		header.className = "header";
		header.appendChild(left_button)
		header.appendChild(year_month_view)
		header.appendChild(right_button)
		let month = document.createElement("table");
		let weeks = new Array(6);
		let days = new Array(7 * 6);
		let week_days = document.createElement("tr");
		month.appendChild(week_days);
		for (let i = 0; i < 7; i++) {
			let week_day = document.createElement("th");
			week_day.className = week_day_class[i];
			week_day.innerText = week_day_name[i];
			week_days.appendChild(week_day);
		}
		for (let i = 0; i < weeks.length; i++) {
			let week = document.createElement("tr");
			weeks[i] = week;
			month.appendChild(week);
		}
		for (let i = 0; i < days.length; i++) {
			let week = weeks[Math.floor(i / 7)];
			let day = document.createElement("td");
			const week_day_index = i % 7;
			day.className = week_day_class[week_day_index];
			day.innerText = i.toString();
			days[i] = day;
			day.addEventListener("click", event => {
				if (this.select_day_callback != null) {
					select_day_callback(this.yeaer_month.getFullYear(), this.yeaer_month.getMonth(), Number(event.target.innerText), week_day_index);
				}
			});
			week.appendChild(day);
		}
		this.select_day_callback = select_day_callback;
		this.year_month_view = year_month_view;
		this.days = days;
		this.frame.appendChild(header);
		this.frame.appendChild(month);
		parent.appendChild(this.frame);
		let today = CalendarUI.#getToday();
		this.yeaer_month = new Date(today.getFullYear(), today.getMonth());
		this.ViewMonth(this.yeaer_month.getFullYear(), this.yeaer_month.getMonth(), today);
		left_button.addEventListener("click", e => {
			this.yeaer_month.setMonth(this.yeaer_month.getMonth() - 1);
			this.ViewMonth(this.yeaer_month.getFullYear(), this.yeaer_month.getMonth(), today);
		});
		right_button.addEventListener("click", e => {
			this.yeaer_month.setMonth(this.yeaer_month.getMonth() + 1);
			this.ViewMonth(this.yeaer_month.getFullYear(), this.yeaer_month.getMonth(), today);
		});
	}
	ViewMonth(year, month, today) {
		let start_week_day = (new Date(year, month, 1)).getDay();
		let base_date = new Date(year, month, -start_week_day + 1);
		for (let i = 0; i < this.days.length; i++) {
			this.days[i].innerText = base_date.getDate().toString();
			if (base_date.getMonth() == month) {
				this.days[i].classList.remove("out_of_month");
			} else {
				this.days[i].classList.add("out_of_month");
			}
			if (base_date.getTime() == today.getTime()) {
				this.days[i].classList.add("today");
			} else {
				this.days[i].classList.remove("today");
			}
			base_date.setDate(base_date.getDate() + 1);
		}
		this.year_month_view.innerText = year.toString() + "年" + (month + 1).toString() + "月";
	}
}
