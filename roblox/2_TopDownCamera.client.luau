-- Put this LocalScript into StarterPlayer -> StarterPlayerScripts
-- Name: TopDownCamera

local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local player = Players.LocalPlayer
local camera = workspace.CurrentCamera

local HEIGHT = 36 -- Height of 2D camera above player

camera.CameraType = Enum.CameraType.Scriptable

RunService.RenderStepped:Connect(function()
    local character = player.Character
    if character and character:FindFirstChild("HumanoidRootPart") then
        local hrp = character.HumanoidRootPart
        local targetPos = hrp.Position
        
        -- Lock camera in top-down 2D perspective
        local camPos = targetPos + Vector3.new(0, HEIGHT, 12)
        camera.CFrame = CFrame.new(camPos, targetPos)
    end
end)

print("[IN THE PINES] 2D Top-Down Camera Activated!")
