class TricolorProgressUI {
    static #Draw(canvas_context, width, height, actual, scheduled, expected) {
        if (expected == 0) {
            if (0 < scheduled) {
                expected = scheduled;
            } else {
                expected = 1;
            }
        }
        const width_actual = Math.trunc(width * actual / expected);
        const width_scheduled = Math.trunc(width * scheduled / expected);
        canvas_context.fillStyle = '#d22';
        canvas_context.fillRect(0, 0, width, height);
        canvas_context.fillStyle = '#286';
        canvas_context.fillRect(0, 0, width_scheduled, height);
        canvas_context.fillStyle = '#4da';
        canvas_context.fillRect(0, 0, width_actual, height);
    }
    constructor(parent, name, width, height) {
        this.holder = document.createElement("div");
        this.holder.className = "TricolorProgressUI";
        this.holder.style.fontSize = `${height}px`;
        this.name_text = document.createElement("span");
        this.name_text.innerText = name;
        this.name_text.className = "name";
        this.progress_time_text = document.createElement("span");
        this.sheduled_time_text = document.createElement("span");
        this.man_minute_text = document.createElement("span");
        this.canvas = document.createElement("canvas");
        this.canvas.className = "TricolorProgressUI";
        this.canvas.width = width;
        this.canvas.height = height;
        this.canvas_context = this.canvas.getContext('2d');
        let delimiter_l = document.createElement("span");
        let delimiter_r = document.createElement("span");
        delimiter_l.innerText = "/";
        delimiter_l.className = "delimiter";
        delimiter_r.innerText = "/";
        delimiter_r.className = "delimiter";
        this.holder.appendChild(this.name_text);
        this.holder.appendChild(this.progress_time_text);
        this.holder.appendChild(delimiter_l);
        this.holder.appendChild(this.sheduled_time_text);
        this.holder.appendChild(delimiter_r);
        this.holder.appendChild(this.man_minute_text);
        this.holder.appendChild(this.canvas);
        parent.appendChild(this.holder);
        TricolorProgressUI.#Draw(this.canvas_context, this.canvas.width, this.canvas.height, 0, 0, 1);
    }
    Update(actual, scheduled, expected) {
        this.progress_time_text.innerText = actual.toString();
        this.sheduled_time_text.innerText = scheduled.toString();
        this.man_minute_text.innerText = expected.toString();
        TricolorProgressUI.#Draw(this.canvas_context, this.canvas.width, this.canvas.height, actual, scheduled, expected);
    }
}
