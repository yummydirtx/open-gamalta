# **Gamalta BLE Protocol Specification**

Version: 1.0.0  
Device: Gamalta 26W Smart Bluetooth Aquarium Light

## **1\. Connection & Auth**

The device uses a standard BLE UART Service but requires a handshake.

* **Service UUID:** 0000fff0-0000-1000-8000-00805f9b34fb  
* **Write Char:** 0000fff3-0000-1000-8000-00805f9b34fb  
* **Notify Char:** 0000fff4-0000-1000-8000-00805f9b34fb

### **Handshake Sequence**

1. **Login:** A5 \[Seq\] 10 07 02 31 32 33 34 35 36 (Password: "123456")  
2. **Time Sync:** A5 \[Seq\] 16 07 \[YY\] \[MM\] \[DD\] \[HH\] \[mm\] \[ss\] (Year is 20XX \- 2000\)

## **2\. Basic Control**

All packets begin with Header 0xA5 and a Sequence Byte.

| Function | Command | Structure | Notes |
| :---- | :---- | :---- | :---- |
| **Power** | 0x01 | 01 03 \[01=ON, 02=OFF\] 00 00 |  |
| **Color** | 0x50 | 50 06 \[R\] \[G\] \[B\] \[W\] \[C\] 01 | Sets static color. |
| **Brightness** | 0x52 | 52 01 \[0-100\] | Global brightness %. |
| **Set Mode** | 0x6A | 6A 01 \[ID\] | 01=Manual, 02=Coral, 03=Fish, 04=Waterweed |

## **3\. Lightning Effect Configuration**

Command: 0x76  
Mask: 0x07  
This command configures the automatic lightning storm schedule.

| Byte | Name | Description |
| :---- | :---- | :---- |
| **4** | **Intensity** | 0x00 \- 0x64 (0-100%). **Special:** 0xFE triggers "Preview Mode". |
| **5** | **Frequency** | 0x00 \- 0x0A (0-10). Flashes per second/interval. |
| **6** | **Start Hour** | 0x00 \- 0x17 (0-23) |
| **7** | **Start Min** | 0x00 \- 0x3B (0-59) |
| **8** | **End Hour** | 0x00 \- 0x17 (0-23) |
| **9** | **End Min** | 0x00 \- 0x3B (0-59) |
| **10** | **Active Days** | Bitmask (See Below) |

### **Active Days Bitmask**

The last byte determines which days the schedule runs, and if the schedule is enabled at all.

* **Bit 0:** Monday  
* **Bit 1:** Tuesday  
* **Bit 2:** Wednesday  
* **Bit 3:** Thursday  
* **Bit 4:** Friday  
* **Bit 5:** Saturday  
* **Bit 6:** Sunday  
* **Bit 7:** **Master Enable** (1 \= On, 0 \= Off)

**Examples:**

* 0xFF (11111111): Enabled every day.  
* 0x7F (01111111): Disabled (Master switch off), but all days selected.  
* 0xFE (11111110): Enabled, but skip Monday.