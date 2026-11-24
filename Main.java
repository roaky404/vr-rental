import java.time.LocalDate;

enum EquipmentStatus {
    AVAILABLE, BOOKED, MAINTENANCE, BUFFER
}

class Equipment {
    private int id;
    private String serialNumber;
    private EquipmentStatus status;
    private int batteryLevel;

    public Equipment(int id, String serialNumber, EquipmentStatus status, int batteryLevel) {
        this.id = id;
        this.serialNumber = serialNumber;
        this.status = status;
        this.batteryLevel = batteryLevel;
    }

    public boolean isAvailable() {
        return this.status == EquipmentStatus.AVAILABLE;
    }

    public boolean hasEnoughBattery() {
        return this.batteryLevel >= 50;
    }

    public void updateStatus(EquipmentStatus newStatus) {
        this.status = newStatus;
    }

    public String getSerialNumber() {
        return serialNumber;
    }

    public int getId() {
        return id;
    }

    public EquipmentStatus getStatus() {
        return status;
    }

    public int getBatteryLevel() {
        return batteryLevel;
    }
}

class BookingRequest {
    private int equipmentId;
    private LocalDate startDate;
    private LocalDate endDate;

    public BookingRequest(int equipmentId, LocalDate startDate, LocalDate endDate) {
        this.equipmentId = equipmentId;
        this.startDate = startDate;
        this.endDate = endDate;
    }

    public int getEquipmentId() {
        return equipmentId;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public LocalDate getEndDate() {
        return endDate;
    }
}

class BookingResult {
    private boolean success;
    private String message;

    public BookingResult(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    public boolean isSuccess() {
        return success;
    }

    public String getMessage() {
        return message;
    }
}

class BookingService {
    private Equipment equipment;

    public BookingService(Equipment equipment) {
        this.equipment = equipment;
    }

    public BookingResult createBooking(BookingRequest request) {
        // проверка, что оборудование существует
        if (this.equipment == null) {
            return new BookingResult(false, "Оборудование не найдено");
        }

        // проверка статуса
        if (!this.equipment.isAvailable()) {
            return new BookingResult(false,
                "Оборудование " + this.equipment.getSerialNumber() + 
                " недоступно. Статус: " + this.equipment.getStatus());
        }

        // проверка заряда батареи
        if (!this.equipment.hasEnoughBattery()) {
            return new BookingResult(false,
                "Оборудование " + this.equipment.getSerialNumber() + 
                " разряжено. Заряд: " + this.equipment.getBatteryLevel() + "%");
        }

        // всё ок, бронируем
        this.equipment.updateStatus(EquipmentStatus.BOOKED);
        return new BookingResult(true,
            "Бронирование создано. Оборудование: " + this.equipment.getSerialNumber()
            + ", период: " + request.getStartDate() + " - " + request.getEndDate());
    }
}

public class Main {
    public static void main(String[] args) {
        // создаём тестовое оборудование
        Equipment vrHeadset = new Equipment(1, "MQ3-001-A", EquipmentStatus.AVAILABLE, 95);
        Equipment brokenHeadset = new Equipment(2, "MQ3-002-B", EquipmentStatus.MAINTENANCE, 40);
        Equipment lowBattery = new Equipment(3, "HV-003-C", EquipmentStatus.AVAILABLE, 20);

        BookingService service = new BookingService(vrHeadset);
        BookingService serviceBroken = new BookingService(brokenHeadset);
        BookingService serviceLowBat = new BookingService(lowBattery);

        BookingRequest request = new BookingRequest(
            1, LocalDate.of(2026, 11, 20), LocalDate.of(2026, 11, 22));

        // тест 1: нормальное бронирование
        BookingResult res1 = service.createBooking(request);
        System.out.println("Тест 1 (доступное): " + (res1.isSuccess() ? "УСПЕХ" : "ОШИБКА"));
        System.out.println(res1.getMessage());
        System.out.println();

        // тест 2: оборудование в ремонте
        BookingResult res2 = serviceBroken.createBooking(request);
        System.out.println("Тест 2 (в ремонте): " + (res2.isSuccess() ? "УСПЕХ" : "ОШИБКА"));
        System.out.println(res2.getMessage());
        System.out.println();

        // тест 3: низкий заряд батареи
        BookingResult res3 = serviceLowBat.createBooking(request);
        System.out.println("Тест 3 (низкий заряд): " + (res3.isSuccess() ? "УСПЕХ" : "ОШИБКА"));
        System.out.println(res3.getMessage());
    }
}