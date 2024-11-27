class CinapsTaskNode {
    constructor(parent, id, name, left, top, width, height, assigne_member_icon) {
        this.holder = document.createElement("div");
        this.holder.id = id;
        this.holder.style.left = `${left}px`;
        this.holder.style.top = `${top}px`;
        this.holder.style.width = `${width}px`;
        this.holder.style.height = `${height}px`;
        this.holder.style.borderRadius = `${parseInt(height / 2)}px`;
        this.holder.tabIndex = 0;
        this.holder.className = "CinapsTaskNode";
        this.holder.innerHTML = name;
        parent.appendChild(this.holder);
        if (assigne_member_icon !== null) {
            const icon = document.createElement("div");
            icon.style.left = `${width - 40}px`;
            icon.style.top = `${parseInt(height / 2)}px`;
            icon.className = "CinapsMemberIcon";
            icon.innerHTML = assigne_member_icon;
            this.holder.appendChild(icon);
        }
    }
    GetElement() {
        return this.holder;
    }
}

class CinapsDeliverableNode {
    constructor(parent, id, name, left, top, width, height) {
        this.holder = document.createElement("div");
        this.holder.id = id;
        this.holder.style.left = `${left}px`;
        this.holder.style.top = `${top}px`;
        this.holder.style.width = `${width}px`;
        this.holder.style.height = `${height}px`;
        this.holder.style.position = "absolute";
        this.holder.style.borderRadius = `${parseInt(height / 2)}px`;
        this.holder.style.display = "flex";
        this.holder.style.alignItems = "center";
        this.holder.style.justifyContent = "center";
        this.holder.tabIndex = 0;
        this.holder.className = "CinapsDeliverableNode";
        this.holder.innerHTML = name;
        parent.appendChild(this.holder);
    }
    GetElement() {
        return this.holder;
    }
}


