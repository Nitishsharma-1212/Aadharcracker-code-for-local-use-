import os
import sys
import time
import string
import multiprocessing as mp
import fitz  
from tqdm import tqdm
import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright

def banner():
    os.system("clear" if os.name == "posix" else "cls")
    print("="*60)
    print("          SUBTLE0 - ULTRACODE MASTER TOOL")
    print("="*60)
    print("[+] SUPER FAST AADHAAR PDF BRUTEFORCE")
    print("[+] CREATOR: @Subtle0")
    print("="*60)
    print("[1] Download Aadhaar PDF (OTP method)")
    print("[2] Crack PDF Password (Bruteforce method)")
    print("[3] Exit")
    print("="*60)

class AadhaarOTPHandler:
    def __init__(self):
        self.eid = None
        self.otp_code = None
        self.pdf_path = None
        
    async def get_eid(self, name, mobile, dob):
        """Retrieve EID from UIDAI"""
        print("\n🔍 RETRIEVING EID...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            await page.goto("https://myaadhaar.uidai.gov.in/retrieve-eid-uid")
            
            # Fill details
            await page.get_by_label("Enrolment ID Number/ SID").check()
            await page.fill("input[placeholder*='Name']", name)
            await page.fill("input[type='date']", dob)
            await page.fill("input[placeholder*='Mobile']", mobile)
            
            print("🔐 Complete captcha...")
            input("Press Enter after captcha...")
            
            await page.get_by_role("button", name="Send OTP").click()
            
            self.otp_code = input("📨 Enter OTP: ").strip()
            await page.fill("input[placeholder*='OTP']", self.otp_code)
            await page.get_by_role("button", name="Verify").click()
            
            await page.wait_for_timeout(5000)
            content = await page.content()
            match = re.search(r'\b\d{28}\b', content)
            
            if match:
                self.eid = match.group(0)
                print(f"✅ EID Found: {self.eid}")
                await browser.close()
                return True
            else:
                print("❌ EID not found")
                await browser.close()
                return False
    
    async def download_pdf(self, name, pincode):
        """Download Aadhaar PDF using EID"""
        print("\n📄 DOWNLOADING AADHAAR PDF...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            await page.goto("https://myaadhaar.uidai.gov.in/download-aadhaar")
            
            await page.get_by_label("I have Enrolment ID (EID)").check()
            await page.fill("input[placeholder*='Enrolment ID']", self.eid)
            await page.fill("input[placeholder*='Full Name']", name)
            await page.fill("input[placeholder*='PIN']", pincode)
            
            print("🔐 Complete captcha...")
            input("Press Enter after captcha...")
            
            await page.get_by_role("button", name="Send OTP").click()
            
            self.otp_code = input("📨 Enter OTP for download: ").strip()
            await page.fill("input[placeholder*='OTP']", self.otp_code)
            await page.get_by_role("button", name="Verify").click()
            
            await page.wait_for_selector("button:has-text('Download Aadhaar')", timeout=30000)
            
            async with page.expect_download() as download_info:
                await page.get_by_role("button", name="Download Aadhaar").click()
            
            download = await download_info.value
            self.pdf_path = Path.cwd() / download.suggested_filename
            await download.save_as(self.pdf_path)
            
            print(f"✅ PDF Downloaded: {self.pdf_path}")
            await browser.close()
            return True
    
    def unlock_pdf(self, name, birth_year):
        """Unlock downloaded PDF"""
        print("\n🔓 UNLOCKING PDF...")
        
        name_prefix = name.upper()[:4].replace(" ", "")
        passwords = [
            f"{name_prefix}{birth_year}",
            f"{name_prefix}{birth_year}@",
            f"{name_prefix}{str(birth_year)[-2:]}",
            name.upper().split()[0][:4] + str(birth_year),
        ]
        
        try:
            doc = fitz.open(self.pdf_path)
        except Exception as e:
            print(f"❌ Failed to open PDF for unlocking: {e}")
            return False

        for pwd in passwords:
            if doc.authenticate(pwd):
                unlocked_path = self.pdf_path.with_name(f"{self.pdf_path.stem}_unlocked.pdf")
                doc.save(unlocked_path)
                print(f"✅ UNLOCKED! Password: {pwd}")
                print(f"📁 Saved: {unlocked_path}")
                return True
        
        print("❌ Could not unlock automatically with basic common passwords.")
        print("💡 Use Option 2 (Bruteforce) from the main menu to crack it!")
        return False
    
    async def run(self):
        print("\n--- AADHAAR OTP DOWNLOADER ---")
        
        name = input("👤 Enter name as on Aadhaar: ").strip()
        mobile = input("📱 Registered mobile number: ").strip()
        dob = input("📅 Date of Birth (YYYY-MM-DD): ").strip()
        pincode = input("📍 PIN Code: ").strip()
        
        try:
            match = re.search(r'\d{4}', dob)
            birth_year = int(match.group()) if match else 1990
        except:
            birth_year = 1990
            
        if not await self.get_eid(name, mobile, dob):
            print("❌ Failed to retrieve EID")
            return
        
        if not await self.download_pdf(name, pincode):
            print("❌ Failed to download PDF")
            return
        
        self.unlock_pdf(name, birth_year)

def worker(pdf_path, chunk_letters, start_year, end_year, found_event, queue):
    """
    Worker process that generates passwords in memory and tests them instantly using PyMuPDF.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        queue.put({"error": f"Failed to open PDF: {str(e)}"})
        return

    tested = 0
    all_letters = string.ascii_uppercase

    for first_letter in chunk_letters:
        if found_event.is_set():
            return
        
        for c2 in all_letters:
            for c3 in all_letters:
                for c4 in all_letters:
                    prefix = first_letter + c2 + c3 + c4
                    
                    for year in range(start_year, end_year + 1):
                        if found_event.is_set():
                            return
                        
                        password = prefix + str(year)
                        
                        if doc.authenticate(password):
                            found_event.set()
                            queue.put({"found": True, "password": password})
                            return
                        
                        tested += 1
                        
                        if tested % 10000 == 0:
                            queue.put({"tested": 10000})

    if tested % 10000 != 0:
        queue.put({"tested": tested % 10000})

def run_bruteforce():
    print("\n" + "-"*40)
    print("💀 ULTRA FAST RAM CRACKING STARTED")
    print("-"*40)
    
    pdf_path = input("[?] Target PDF Path (e.g. file.pdf): ").strip()
    if not os.path.exists(pdf_path):
        print("❌ Error: File not found!")
        return

    try:
        start_year = int(input("[?] Start Year (e.g. 1950): ").strip())
        end_year = int(input("[?] End Year (e.g. 2026): ").strip())
    except ValueError:
        print("❌ Error: Invalid Year format!")
        return

    first_letter = input("[?] Name ka 1st Letter (optional, hit enter to skip): ").strip().upper()

    print("\n[*] Initializing RAM Generator & Threads...")
    time.sleep(1)

    if first_letter and first_letter in string.ascii_uppercase:
        letters_to_process = [first_letter]
    else:
        letters_to_process = list(string.ascii_uppercase)
    
    total_combs = len(letters_to_process) * (26**3) * (end_year - start_year + 1)
    
    try:
        user_threads = input(f"[?] Enter number of threads (1-{mp.cpu_count()}, default 8): ").strip()
        if user_threads == "":
            threads = min(8, mp.cpu_count())
        else:
            threads = int(user_threads)
    except ValueError:
        threads = min(8, mp.cpu_count())
        
    if threads > len(letters_to_process):
        threads = len(letters_to_process)
        
    print(f"[+] Total Passwords to test : {total_combs:,}")
    print(f"[+] Active CPU Threads      : {threads}")
    print("[*] Attack Launched... \n")
    
    manager = mp.Manager()
    found_event = manager.Event()
    queue = manager.Queue()
    
    chunks = [[] for _ in range(threads)]
    for i, letter in enumerate(letters_to_process):
        chunks[i % threads].append(letter)
        
    processes = []
    for chunk in chunks:
        if chunk:
            p = mp.Process(target=worker, args=(pdf_path, chunk, start_year, end_year, found_event, queue))
            p.start()
            processes.append(p)
            
    progress = tqdm(total=total_combs, desc="💀 CRACKING", unit=" keys", colour="red")
    
    found_password = None
    
    while any(p.is_alive() for p in processes) or not queue.empty():
        try:
            msg = queue.get(timeout=0.5)
            if "found" in msg:
                found_password = msg["password"]
                found_event.set()
                break
            elif "tested" in msg:
                progress.update(msg["tested"])
            elif "error" in msg:
                print(f"\n[!] Thread Error: {msg['error']}")
        except:
            pass
            
    progress.close()
    
    for p in processes:
        p.terminate()
        p.join()
        
    print("\n" + "="*60)
    if found_password:
        print(f"🔥 MISSION SUCCESS! PASSWORD FOUND: {found_password} 🔥")
        
        try:
            doc = fitz.open(pdf_path)
            doc.authenticate(found_password)
            output_name = "UNLOCKED_" + os.path.basename(pdf_path)
            doc.save(output_name)
            print(f"[+] Unlocked file saved as: {output_name}")
        except Exception as e:
            print(f"[-] Could not save unlocked file automatically: {e}")
            
    else:
        print("❌ MISSION FAILED: Password not found in given range.")
    print("="*60 + "\n")

def run_downloader():
    handler = AadhaarOTPHandler()
    asyncio.run(handler.run())

def main():
    try:
        while True:
            banner()
            choice = input("\n[?] Enter your choice (1/2/3): ").strip()
            
            if choice == '1':
                run_downloader()
                input("\nPress Enter to return to Menu...")
                
            elif choice == '2':
                run_bruteforce()
                input("\nPress Enter to return to Menu...")
                
            elif choice == '3':
                print("\n[!] Exiting System... 💀")
                break
            else:
                print("\n❌ Invalid choice!")
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[!] Script stopped by User. 💀")
        sys.exit()

if __name__ == "__main__":
    main()
