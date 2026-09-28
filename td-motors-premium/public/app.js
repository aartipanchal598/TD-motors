const DEMO_WHATSAPP = "919577230707"; // Replace with verified TD Motors WhatsApp number

const cars = [
  {brand:"Tata Motors", name:"Premium SUV", type:"SUV", fuel:"Petrol", transmission:"Automatic", price:"Price on enquiry", image:"https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?auto=format&fit=crop&w=1000&q=85"},
  {brand:"Hyundai", name:"Premium Sedan", type:"Sedan", fuel:"Petrol", transmission:"Automatic", price:"Price on enquiry", image:"https://images.unsplash.com/photo-1619767886558-efdc259cde1a?auto=format&fit=crop&w=1000&q=85"},
  {brand:"Mahindra", name:"Adventure SUV", type:"SUV", fuel:"Diesel", transmission:"Manual", price:"Price on enquiry", image:"https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?auto=format&fit=crop&w=1000&q=85"},
  {brand:"Kia", name:"Urban SUV", type:"SUV", fuel:"Petrol", transmission:"Automatic", price:"Price on enquiry", image:"https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?auto=format&fit=crop&w=1000&q=85"},
  {brand:"Toyota", name:"Premium Hybrid", type:"Sedan", fuel:"Hybrid", transmission:"Automatic", price:"Price on enquiry", image:"https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1000&q=85"},
  {brand:"Maruti Suzuki", name:"City Hatchback", type:"Hatchback", fuel:"Petrol", transmission:"Automatic", price:"Price on enquiry", image:"https://images.unsplash.com/photo-1590362891991-f776e747a588?auto=format&fit=crop&w=1000&q=85"},
  {brand:"EV Collection", name:"Electric Drive", type:"EV", fuel:"Electric", transmission:"Automatic", price:"Price on enquiry", image:"https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1000&q=85"}
];

const detailServices = [
  ["01","Car Detailing","Deep exterior + interior care for a refreshed finish."],
  ["02","Ceramic Coating","Long-term paint protection with a premium gloss."],
  ["03","PPF","Paint protection film for high-impact areas and surfaces."],
  ["04","Paint Correction","Careful correction to improve clarity and finish."],
  ["05","Interior Detailing","Detailed cleaning and care for the cabin."],
  ["06","Exterior Detailing","Wash, decontamination and finishing treatment."],
  ["07","Car Polishing","Gloss enhancement and surface refinement."],
  ["08","Premium Car Wash","A more considered clean for your daily drive."]
];

const workshopServices = [
  ["01","General Service","Routine checks and maintenance for dependable driving."],
  ["02","Periodic Maintenance","Scheduled care based on vehicle requirements."],
  ["03","Engine Diagnostics","Identify warning signs and diagnostic issues."],
  ["04","Brake Service","Inspection and maintenance of braking components."],
  ["05","AC Service","Air-conditioning inspection and service."],
  ["06","Battery Check","Battery health and starting-system checks."],
  ["07","Wheel Alignment","Alignment checks for balanced handling and tyre wear."],
  ["08","Suspension","Inspection of suspension components and ride quality."],
  ["09","Electrical Repairs","Electrical diagnosis and repair support."],
  ["10","Oil Change","Engine oil and routine lubrication service."],
  ["11","Car Inspection","Vehicle condition inspection before your next drive."],
  ["12","Other Repairs","Send an enquiry for a specific requirement."]
];

const carGrid = document.getElementById("carGrid");
function renderCars(filter="all"){
  carGrid.innerHTML = cars.filter(c=>filter==="all" || c.type===filter).map(c=>`
    <article class="car-card">
      <div class="car-image"><img src="${c.image}" alt="${c.brand} ${c.name}" loading="lazy"><span class="car-tag">${c.type}</span></div>
      <div class="car-info">
        <div class="brand">${c.brand}</div><h3>${c.name}</h3><div class="specs"><span>${c.fuel}</span><span>${c.transmission}</span></div>
        <strong>${c.price}</strong>
        <div class="card-actions"><a href="#inquiry" data-car="${c.name}" data-brand="${c.brand}">Enquire</a><a href="#inquiry" data-service="Test Drive" data-car="${c.name}" data-brand="${c.brand}">Test Drive</a></div>
      </div>
    </article>`).join("");
}
renderCars();
document.querySelectorAll(".filter").forEach(btn=>btn.addEventListener("click",()=>{
  document.querySelectorAll(".filter").forEach(b=>b.classList.remove("active")); btn.classList.add("active"); renderCars(btn.dataset.filter);
}));

document.getElementById("detailServices").innerHTML = detailServices.map(s=>`<article class="service-card"><b>${s[0]}</b><h3>${s[1]}</h3><p>${s[2]}</p></article>`).join("");
document.getElementById("workshopServices").innerHTML = workshopServices.map(s=>`<article class="workshop-service"><b>${s[0]}</b><h3>${s[1]}</h3><p>${s[2]}</p></article>`).join("");

const navLinks=document.getElementById("navLinks"), menuBtn=document.getElementById("menuBtn");
menuBtn.addEventListener("click",()=>navLinks.classList.toggle("open"));
navLinks.querySelectorAll("a").forEach(a=>a.addEventListener("click",()=>navLinks.classList.remove("open")));

window.addEventListener("load",()=>setTimeout(()=>document.getElementById("loader").classList.add("hide"),500));

const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add("visible")}),{threshold:.12});
document.querySelectorAll(".reveal").forEach(el=>observer.observe(el));

const baRange=document.getElementById("baRange"), before=document.querySelector(".ba-before"), line=document.querySelector(".ba-line");
baRange.addEventListener("input",e=>{before.style.width=e.target.value+"%";line.style.left=e.target.value+"%"});

const testimonials=[
 ["Replace this demo testimonial with a verified TD Motors customer review before launch.","Customer Review"],
 ["Add another verified customer review here before production launch.","Customer Review"],
 ["Add a third verified customer review here before production launch.","Customer Review"]
];
let ti=0;
function showTest(){document.getElementById("testimonialText").textContent=testimonials[ti][0];document.getElementById("testimonialName").textContent=testimonials[ti][1]}
document.getElementById("nextTest").onclick=()=>{ti=(ti+1)%testimonials.length;showTest()};
document.getElementById("prevTest").onclick=()=>{ti=(ti-1+testimonials.length)%testimonials.length;showTest()};

function buildWhatsAppMessage(data){
 return `Hello, I am ${data.fullName}.
I am interested in ${data.carModel || data.brand || "TD Motors services"}.
My requirement is ${data.serviceRequired}.
${data.message ? "Additional requirement: "+data.message : ""}
Please contact me regarding this inquiry.`;
}
function openWhatsApp(){
 const form=document.getElementById("inquiryForm"), data=Object.fromEntries(new FormData(form).entries());
 if(!data.fullName || !data.serviceRequired){document.getElementById("formMessage").textContent="Please enter your name and select a requirement first.";return}
 if(DEMO_WHATSAPP.includes("X")){document.getElementById("formMessage").textContent="Add the verified TD Motors WhatsApp number in app.js first.";return}
 window.open(`https://wa.me/${DEMO_WHATSAPP}?text=${encodeURIComponent(buildWhatsAppMessage(data))}`,"_blank");
}
document.getElementById("whatsappBtn").addEventListener("click",openWhatsApp);
document.getElementById("floatingWa").addEventListener("click",e=>{e.preventDefault(); if(DEMO_WHATSAPP.includes("X")) alert("Replace DEMO_WHATSAPP in app.js with the verified TD Motors number."); else window.open(`https://wa.me/${DEMO_WHATSAPP}`,"_blank")});

document.addEventListener("click",e=>{
 const el=e.target.closest("[data-service],[data-car],[data-brand]");
 if(!el)return;
 const form=document.getElementById("inquiryForm");
 if(el.dataset.service)form.serviceRequired.value=el.dataset.service;
 if(el.dataset.car)form.carModel.value=el.dataset.car;
 if(el.dataset.brand)form.brand.value=el.dataset.brand;
});

document.getElementById("inquiryForm").addEventListener("submit",async e=>{
 e.preventDefault();
 const form=e.currentTarget,msg=document.getElementById("formMessage"),btn=form.querySelector(".submit-btn");
 if(!form.checkValidity()){form.reportValidity();return}
 const mobile=form.mobile.value.replace(/\D/g,"");
 if(mobile.length<10){msg.textContent="Please enter a valid mobile number.";return}
 btn.disabled=true;btn.textContent="Submitting...";
 try{
   const response=await fetch("/api/inquiries",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(form).entries()))});
   const result=await response.json();
   if(!response.ok)throw new Error(result.message);
   msg.textContent="Inquiry submitted successfully. You can also continue on WhatsApp.";
   form.reset();
 }catch(err){msg.textContent=err.message||"Submission failed. Please try WhatsApp."}
 finally{btn.disabled=false;btn.innerHTML='Submit Inquiry <span>↗</span>'}
});
