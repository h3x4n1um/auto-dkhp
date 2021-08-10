# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import aiohttp
import asyncio
import copy
import getpass
import os

list_txtMaMonHoc = ["CT109", "CT214"]
list_hidMaNhom = ["01", "01"]
list_hidSoTinChi = ["3", "3"]

dkhp_template = {
    "txtMaMonHoc": '',
    "hidMaNhom": '',
    "hidSoTinChi": '',
    "cboHocKyMain": '',
    "txtTKB": '1',
    "hidMethod": "regdetails",
    "hdKey": ''
}

username = str()
password = str()

async def async_request(method: str, client: aiohttp.ClientSession, url: str, data = None):
    while True:
        try:
            async with client.request(method, url, data=data) as resp:
                res = await resp.text()
                #print(url)
                #print(res)
                return res
        except Exception:
            print("Patience is virtue")
            await asyncio.sleep(1)

async def login_htql(client: aiohttp.ClientSession) -> None:
    login = {
        "txtDinhDanh": username,
        "txtMatKhau": password
    }
    login_resp = await async_request("POST", client, "https://qldt.ctu.edu.vn/htql/sinhvien/dang_nhap.php", login)
    if "logout.php" in login_resp:
        raise ValueError("Tài khoản hoặc mật khẩu không đúng!")

    login_dkhp = copy.deepcopy(login)
    login_dkhp["txtMatKhau"] = 'p'
    await async_request("POST", client, "https://qldt.ctu.edu.vn/htql/dkmh/student/dang_nhap.php", login_dkhp)

async def get_form_data(client: aiohttp.ClientSession) -> None:
    while True:
        try:
            soup = BeautifulSoup(
                await async_request(
                    "GET",
                    client,
                    "https://qldt.ctu.edu.vn/htql/dkmh/student/index.php?action=dky_mhoc"
                ),
                "lxml"
            )
            dkhp_template["cboHocKyMain"] = soup.find(id="cboHocKyMain")["value"]
            return
        except TypeError:
            print("Không thể lấy thông tin từ form")

async def dkhp(client: aiohttp.ClientSession, txtMaMonHoc: str, hidMaNhom: str, hidSoTinChi: str) -> None:
    data = copy.deepcopy(dkhp_template)
    data["txtMaMonHoc"] = txtMaMonHoc
    data["hidMaNhom"] = hidMaNhom
    data["hidSoTinChi"] = hidSoTinChi
    
    await async_request("POST", client, "https://qldt.ctu.edu.vn/htql/dkmh/student/index.php?action=dky_mhoc", data=data)

async def main() -> None:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=5),
        raise_for_status=True
    ) as client:
        await login_htql(client)
        await get_form_data(client)
        await asyncio.gather(*[dkhp(client, list_txtMaMonHoc[i], list_hidMaNhom[i], list_hidSoTinChi[i]) for i in range(len(list_txtMaMonHoc))])

if __name__ == "__main__":
    # Windows workaround for asyncio
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print("\nTool dkhp made by H3x4n1um")
    
    if list_txtMaMonHoc:
        print("\nHọc phần\tNhóm\tSố tín chỉ")
        for i in range(len(list_txtMaMonHoc)):
            print("{}\t\t{}\t{}".format(list_txtMaMonHoc[i], list_hidMaNhom[i], list_hidSoTinChi[i]))

        username = input("\nUsername: ").lower()
        password = getpass.getpass()
        
        print()
        
        try:
            asyncio.run(main())
            print("Done!")
        except Exception as e:
            print(e)
    else:
        print("\nCó vẻ bạn chưa nhập data vào tool")
